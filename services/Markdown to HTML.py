import markdown as md
import streamlit as st
import streamlit.components.v1 as components
from translations import translations

CSS = (
    "<style>body{font-family:'Segoe UI',Arial,sans-serif;line-height:1.6;color:#1f2937;"
    "max-width:720px;margin:auto;padding:16px}"
    "h1,h2,h3{color:#111827}"
    "a{color:#4361ee}"
    "code{background:#f3f4f6;padding:2px 5px;border-radius:4px;font-size:0.9em}"
    "pre{background:#f3f4f6;padding:12px;border-radius:8px;overflow:auto}"
    "blockquote{border-left:3px solid #4361ee;margin:0;padding-left:12px;color:#6b7280}"
    "table{border-collapse:collapse}th,td{border:1px solid #e5e7eb;padding:6px 10px}</style>"
)


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["md2html_title"])

    src = st.text_area(t["md2html_input"], height=260, placeholder="# Hello\n\nSome **markdown**...")

    if not st.button("➡️ " + t["md2html_convert"]):
        return
    if not src.strip():
        st.warning(t["md2html_empty"])
        return

    body = md.markdown(src, extensions=["extra", "tables", "fenced_code", "sane_lists"])
    full = f"<!doctype html><html><head><meta charset='utf-8'>{CSS}</head><body>{body}</body></html>"

    st.subheader(t["preview"])
    components.html(full, height=420, scrolling=True)
    st.download_button("⬇️ " + t["md2html_download"], full, file_name="document.html", mime="text/html")
    st.code(full, language="html")
