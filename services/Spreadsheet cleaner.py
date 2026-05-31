import io
import re
import pandas as pd
import streamlit as st
from translations import translations


def _snake(name):
    s = re.sub(r"\s+", "_", str(name).strip())
    s = re.sub(r"[^\w]", "", s)
    return s.lower() or "column"


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["clean_title"])

    up = st.file_uploader(t["clean_upload"], type=["csv", "xlsx", "xls"])
    if not up:
        return

    is_csv = up.name.lower().endswith(".csv")
    try:
        df = pd.read_csv(up) if is_csv else pd.read_excel(up)
    except Exception as e:
        st.error(f"{t['clean_error']} {e}")
        return

    st.subheader(t["clean_before"])
    st.dataframe(df.head(50), use_container_width=True)

    st.markdown(f"**{t['clean_options']}**")
    trim = st.checkbox(t["clean_trim"], value=True)
    drop_empty = st.checkbox(t["clean_drop_empty"], value=True)
    dedupe = st.checkbox(t["clean_dedupe"], value=True)
    headers = st.checkbox(t["clean_headers"], value=False)

    if not st.button("🧹 " + t["clean_run"]):
        return

    out = df.copy()
    if trim:
        for c in out.select_dtypes(include="object"):
            out[c] = out[c].map(lambda v: v.strip() if isinstance(v, str) else v)
    if drop_empty:
        out = out.dropna(axis=0, how="all").dropna(axis=1, how="all")
    if dedupe:
        out = out.drop_duplicates()
    if headers:
        out.columns = [_snake(c) for c in out.columns]

    st.subheader(t["clean_after"])
    st.dataframe(out.head(50), use_container_width=True)
    st.success(f"{t['clean_rows_removed']}: {len(df) - len(out)}")

    buf = io.BytesIO()
    if is_csv:
        out.to_csv(buf, index=False)
        fname, mime = "cleaned.csv", "text/csv"
    else:
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            out.to_excel(w, index=False)
        fname = "cleaned.xlsx"
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    st.download_button("⬇️ " + t["clean_download"], buf.getvalue(), file_name=fname, mime=mime)
