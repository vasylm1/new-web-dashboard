import io
from PIL import Image
import streamlit as st
from translations import translations

# Page sizes in points (1/72"). None = fit each page to its image.
PAGE_SIZES = {"A4": (595, 842), "Letter": (612, 792), "Fit to image": None}


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["img2pdf_title"])

    files = st.file_uploader(
        t["img2pdf_upload"],
        type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
    )
    page = st.selectbox(t["img2pdf_page"], list(PAGE_SIZES.keys()))
    orientation = st.radio(
        t["img2pdf_orientation"],
        [t["img2pdf_portrait"], t["img2pdf_landscape"]],
        horizontal=True,
    )

    if not st.button("📄 " + t["img2pdf_create"]):
        return
    if not files:
        st.warning(t["img2pdf_empty"])
        return

    pages = []
    size = PAGE_SIZES[page]
    for f in files:
        im = Image.open(f).convert("RGB")
        if size is None:
            pages.append(im)
            continue
        w, h = size
        if orientation == t["img2pdf_landscape"]:
            w, h = h, w
        canvas = Image.new("RGB", (w, h), "white")
        fitted = im.copy()
        fitted.thumbnail((w, h), Image.LANCZOS)
        canvas.paste(fitted, ((w - fitted.width) // 2, (h - fitted.height) // 2))
        pages.append(canvas)

    buf = io.BytesIO()
    pages[0].save(buf, "PDF", save_all=True, append_images=pages[1:])
    st.success(f"✅ {len(pages)}")
    st.download_button("⬇️ " + t["img2pdf_download"], buf.getvalue(), file_name="images.pdf", mime="application/pdf")
