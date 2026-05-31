import io
import os
import re
import tempfile
import markdown as md
import streamlit as st
from ebooklib import epub
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["epub_title"])

    book_title = st.text_input(t["epub_book_title"])
    author = st.text_input(t["epub_author"])
    content = st.text_area(t["epub_content"], height=300, placeholder="# Chapter 1\n\nText...\n\n# Chapter 2\n\nText...")

    if not st.button("📚 " + t["epub_generate"]):
        return
    if not book_title.strip() or not content.strip():
        st.warning(t["epub_empty"])
        return

    # Split on top-level "# " headings into chapters.
    parts = re.split(r"(?m)^#\s+", content)
    sections = [p for p in parts if p.strip()]
    if not sections:
        sections = [content]

    book = epub.EpubBook()
    book.set_title(book_title)
    book.set_language(lang[:2].lower() if lang != "中文" else "zh")
    if author.strip():
        book.add_author(author)

    chapters = []
    for i, sec in enumerate(sections, 1):
        title_line, _, rest = sec.partition("\n")
        ch_title = title_line.strip() or f"Chapter {i}"
        body = md.markdown(rest.strip() or sec.strip())
        ch = epub.EpubHtml(title=ch_title, file_name=f"chap_{i}.xhtml", lang="en")
        ch.content = f"<h1>{ch_title}</h1>{body}"
        book.add_item(ch)
        chapters.append(ch)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".epub")
    tmp.close()
    try:
        epub.write_epub(tmp.name, book)
        with open(tmp.name, "rb") as f:
            data = f.read()
    finally:
        os.unlink(tmp.name)

    st.success("✅")
    st.download_button("⬇️ " + t["epub_download"], data, file_name="book.epub", mime="application/epub+zip")
