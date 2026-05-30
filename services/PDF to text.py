import streamlit as st
from PyPDF2 import PdfReader
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["pdftxt_title"])

    up = st.file_uploader(t["pdftxt_upload"], type=["pdf"])
    if not up:
        return

    if not st.button("📄 " + t["pdftxt_extract"]):
        return
    try:
        reader = PdfReader(up)
    except Exception as e:
        st.error(f"{t['pdftxt_error']} {e}")
        return

    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages).strip()

    st.caption(f"{t['pdftxt_pages']}: {len(pages)}")
    if not text:
        st.warning(t["pdftxt_empty"])
        return

    st.text_area(t["pdftxt_title"], value=text[:5000], height=320, label_visibility="collapsed")
    st.download_button("⬇️ " + t["pdftxt_download"], text, file_name="extracted.txt", mime="text/plain")
