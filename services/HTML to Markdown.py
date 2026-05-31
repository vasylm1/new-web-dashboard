import streamlit as st
from markdownify import markdownify as mdify
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["html2md_title"])

    src = st.text_area(t["html2md_input"], height=240, placeholder="<h1>Title</h1><p>Some <b>HTML</b>...</p>")

    if not src.strip():
        st.info(t["html2md_empty"])
        return

    markdown = mdify(src, heading_style="ATX").strip()
    st.subheader(t["preview"])
    st.code(markdown, language="markdown")
    st.download_button("⬇️ " + t["html2md_download"], markdown, file_name="converted.md", mime="text/markdown")
