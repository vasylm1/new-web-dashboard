import io
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from translations import translations
from pdfutil import make_pdf


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["pdfwm_title"])

    up = st.file_uploader(t["pdfwm_upload"], type=["pdf"])
    text = st.text_input(t["pdfwm_text"], value="DRAFT")
    opacity = st.slider(t["pdfwm_opacity"], 5, 80, 25)

    if not st.button("💧 " + t["pdfwm_apply"]):
        return
    if not up or not text.strip():
        return

    try:
        reader = PdfReader(up)
        page0 = reader.pages[0]
        w, h = float(page0.mediabox.width), float(page0.mediabox.height)

        # Build a single watermark page (points) with diagonal grey text.
        pdf, fam = make_pdf(fmt=(w, h), unit="pt")
        pdf.add_page()
        grey = 255 - int(255 * opacity / 100)
        pdf.set_text_color(grey, grey, grey)
        pdf.set_font(fam, "B", 60)
        with pdf.rotation(45, w / 2, h / 2):
            pdf.set_xy(0, h / 2 - 30)
            pdf.cell(w, 60, text, align="C")
        stamp = PdfReader(io.BytesIO(bytes(pdf.output()))).pages[0]

        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(stamp)
            writer.add_page(page)
        out = io.BytesIO()
        writer.write(out)
    except Exception as e:
        st.error(f"{t['pdfwm_error']} {e}")
        return

    st.download_button("⬇️ " + t["pdfwm_download"], out.getvalue(), file_name="watermarked.pdf", mime="application/pdf")
