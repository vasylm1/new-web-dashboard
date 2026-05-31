import io
import re
from collections import Counter
import pandas as pd
import streamlit as st
from translations import translations

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["elv_title"])

    up = st.file_uploader(t["elv_upload"], type=["csv", "xlsx", "xls"])
    if not up:
        return
    try:
        df = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
    except Exception as e:
        st.error(f"{t['elv_error']} {e}")
        return

    col = st.selectbox(t["elv_column"], list(df.columns))
    if not st.button("✅ " + t["elv_run"]):
        return

    emails = df[col].dropna().astype(str).str.strip().str.lower()
    valid_mask = emails.map(lambda v: bool(EMAIL_RE.match(v)))
    valid = emails[valid_mask]
    invalid = emails[~valid_mask]
    unique_valid = valid.drop_duplicates()
    dup_count = len(valid) - len(unique_valid)

    c1, c2, c3 = st.columns(3)
    c1.metric(t["elv_valid"], len(unique_valid))
    c2.metric(t["elv_invalid"], len(invalid))
    c3.metric(t["elv_duplicates"], dup_count)

    domains = Counter(e.split("@")[1] for e in unique_valid).most_common(8)
    if domains:
        st.subheader(t["elv_domains"])
        st.write("  ·  ".join(f"**{d}** ({n})" for d, n in domains))

    buf = io.BytesIO()
    pd.DataFrame({col: unique_valid}).to_csv(buf, index=False)
    st.download_button("⬇️ " + t["elv_download"], buf.getvalue(), file_name="valid_emails.csv", mime="text/csv")
