import io
import re
import hashlib
import pandas as pd
import streamlit as st
from translations import translations

EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+)")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{6,}\d)")


def _mask_email(m):
    return f"{m.group(1)}***{m.group(2)}"


def _mask_phones(text):
    def repl(m):
        digits = re.sub(r"\D", "", m.group(1))
        keep = digits[-2:] if len(digits) >= 2 else digits
        return "*" * max(0, len(digits) - 2) + keep
    return PHONE_RE.sub(repl, text)


def _hash(value):
    return hashlib.sha1(str(value).encode("utf-8")).hexdigest()[:10]


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["anon_title"])

    up = st.file_uploader(t["anon_upload"], type=["csv", "xlsx", "xls"])
    if not up:
        return
    is_csv = up.name.lower().endswith(".csv")
    try:
        df = pd.read_csv(up) if is_csv else pd.read_excel(up)
    except Exception as e:
        st.error(f"{t['anon_error']} {e}")
        return

    st.dataframe(df.head(20), use_container_width=True)
    st.markdown(f"**{t['anon_options']}**")
    do_emails = st.checkbox(t["anon_emails"], value=True)
    do_phones = st.checkbox(t["anon_phones"], value=True)
    hash_col = st.selectbox(t["anon_names_col"], ["—"] + list(df.columns))

    if not st.button("🕵️ " + t["anon_run"]):
        return
    if not (do_emails or do_phones or hash_col != "—"):
        st.warning(t["anon_none"])
        return

    out = df.copy()
    for c in out.select_dtypes(include="object"):
        if do_emails:
            out[c] = out[c].map(lambda v: EMAIL_RE.sub(_mask_email, v) if isinstance(v, str) else v)
        if do_phones:
            out[c] = out[c].map(lambda v: _mask_phones(v) if isinstance(v, str) else v)
    if hash_col != "—":
        out[hash_col] = out[hash_col].map(_hash)

    st.dataframe(out.head(20), use_container_width=True)
    buf = io.BytesIO()
    if is_csv:
        out.to_csv(buf, index=False)
        fname, mime = "anonymized.csv", "text/csv"
    else:
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            out.to_excel(w, index=False)
        fname = "anonymized.xlsx"
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    st.download_button("⬇️ " + t["anon_download"], buf.getvalue(), file_name=fname, mime=mime)
