import streamlit as st
from translations import translations
from pdfutil import make_pdf, pdf_bytes

PRIMARY = (67, 97, 238)


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["cv_title"])

    name = st.text_input(t["cv_name"])
    headline = st.text_input(t["cv_headline"])
    contact = st.text_input(t["cv_contact"], placeholder="email · phone · city")
    summary = st.text_area(t["cv_summary"], height=90)
    experience = st.text_area(t["cv_experience"], height=120, placeholder="Marketing Manager — Acme Inc. (2023–now)\n...")
    education = st.text_area(t["cv_education"], height=90)
    skills = st.text_input(t["cv_skills"], placeholder="Power BI, SQL, Python")

    if not st.button("📄 " + t["cv_generate"]):
        return
    if not name.strip():
        st.warning(t["cv_empty"])
        return

    pdf, fam = make_pdf()
    pdf.add_page()

    pdf.set_text_color(*PRIMARY)
    pdf.set_font(fam, "B", 24)
    pdf.cell(0, 12, name, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(80, 80, 80)
    pdf.set_font(fam, "", 12)
    if headline:
        pdf.cell(0, 7, headline, new_x="LMARGIN", new_y="NEXT")
    if contact:
        pdf.cell(0, 7, contact, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    def section(title, text, bullets=False):
        if not text.strip():
            return
        pdf.set_text_color(*PRIMARY)
        pdf.set_font(fam, "B", 13)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*PRIMARY)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(2)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font(fam, "", 11)
        for line in text.splitlines():
            if line.strip():
                pdf.multi_cell(0, 6, (f"•  {line.strip()}" if bullets else line.strip()))
        pdf.ln(3)

    section(t["cv_summary"], summary)
    section(t["cv_experience"], experience, bullets=True)
    section(t["cv_education"], education, bullets=True)
    if skills.strip():
        section(t["cv_skills"], skills)

    st.download_button("⬇️ " + t["cv_download"], pdf_bytes(pdf), file_name="resume.pdf", mime="application/pdf")
