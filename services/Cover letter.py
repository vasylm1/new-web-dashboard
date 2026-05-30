from datetime import date
import streamlit as st
from translations import translations
from pdfutil import make_pdf, pdf_bytes


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["cl_title"])

    name = st.text_input(t["cl_name"])
    recipient = st.text_input(t["cl_recipient"], placeholder="Hiring Team, Acme")
    role = st.text_input(t["cl_role"])
    body = st.text_area(t["cl_body"], height=240)

    if not st.button("✉️ " + t["cl_generate"]):
        return
    if not name.strip() or not body.strip():
        st.warning(t["cl_empty"])
        return

    pdf, fam = make_pdf()
    pdf.add_page()
    pdf.set_text_color(30, 30, 30)
    pdf.set_font(fam, "", 11)

    pdf.cell(0, 6, date.today().strftime("%Y-%m-%d"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    if recipient:
        pdf.multi_cell(0, 6, recipient)
    pdf.ln(4)
    if role:
        pdf.set_font(fam, "B", 11)
        pdf.multi_cell(0, 6, role)
        pdf.set_font(fam, "", 11)
        pdf.ln(2)

    for para in body.split("\n\n"):
        pdf.multi_cell(0, 6, para.strip())
        pdf.ln(3)

    pdf.ln(6)
    pdf.multi_cell(0, 6, name)

    st.download_button("⬇️ " + t["cl_download"], pdf_bytes(pdf), file_name="cover_letter.pdf", mime="application/pdf")
