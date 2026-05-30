import streamlit as st
from translations import translations
from pdfutil import make_pdf, pdf_bytes
from tablutil import read_table, template_bytes, TEMPLATE_MIME

PRIMARY = (67, 97, 238)


def _draw(pdf, fam, recipient, text, signer, cdate):
    pdf.add_page()
    pdf.set_draw_color(*PRIMARY)
    pdf.set_line_width(2)
    pdf.rect(10, 10, pdf.w - 20, pdf.h - 20)
    pdf.set_line_width(0.4)
    pdf.rect(14, 14, pdf.w - 28, pdf.h - 28)

    pdf.ln(34)
    pdf.set_text_color(*PRIMARY)
    pdf.set_font(fam, "B", 36)
    pdf.cell(0, 18, "Certificate", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(90, 90, 90)
    pdf.set_font(fam, "", 14)
    pdf.cell(0, 10, "of Achievement", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    pdf.set_text_color(20, 20, 20)
    pdf.set_font(fam, "B", 26)
    pdf.cell(0, 14, recipient, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font(fam, "", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 8, text, align="C")

    pdf.ln(20)
    pdf.set_font(fam, "", 12)
    line = "  |  ".join(filter(None, [signer.strip(), cdate.strip()]))
    if line:
        pdf.cell(0, 8, line, align="C", new_x="LMARGIN", new_y="NEXT")


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["cert_title"])

    mode_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    mode = mode_map[st.radio(t["batch_mode"], list(mode_map.keys()), horizontal=True)]

    # Shared certificate text (applies to everyone in batch mode).
    text = st.text_area(t["cert_text"], value="has successfully completed the course", height=70)
    signer = st.text_input(t["cert_signer"])
    cdate = st.text_input(t["cert_date"])

    if mode == "single":
        recipient = st.text_input(t["cert_recipient"])
        if not st.button("🏆 " + t["cert_generate"]):
            return
        if not recipient.strip():
            st.warning(t["cert_empty"])
            return
        pdf, fam = make_pdf(orientation="L")
        _draw(pdf, fam, recipient, text, signer, cdate)
        st.download_button("⬇️ " + t["cert_download"], pdf_bytes(pdf), file_name="certificate.pdf", mime="application/pdf")
        return

    # Batch mode
    st.download_button(
        "📥 " + t["batch_template"],
        template_bytes(["Name"], [["Jane Doe"], ["Alex Rivera"], ["Sam Kowalski"]]),
        file_name="certificate_template.xlsx", mime=TEMPLATE_MIME,
    )
    up = st.file_uploader(t["batch_upload"], type=["csv", "xlsx", "xls"])
    if not up:
        return
    df = read_table(up)
    col = st.selectbox(t["batch_name_col"], list(df.columns))
    if not st.button("🏆 " + t["batch_generate"]):
        return

    names = [str(v).strip() for v in df[col].dropna() if str(v).strip()]
    if not names:
        st.warning(t["batch_empty"])
        return
    pdf, fam = make_pdf(orientation="L")
    for name in names:
        _draw(pdf, fam, name, text, signer, cdate)
    st.success(f"{t['batch_done']}: {len(names)}")
    st.download_button("⬇️ " + t["cert_download"], pdf_bytes(pdf), file_name="certificates.pdf", mime="application/pdf")
