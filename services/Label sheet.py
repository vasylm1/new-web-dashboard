import streamlit as st
from translations import translations
from pdfutil import make_pdf, pdf_bytes


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["label_title"])

    raw = st.text_area(t["label_input"], height=180, placeholder="Label A\nLabel B\nLabel C")
    c1, c2 = st.columns(2)
    cols = c1.slider(t["label_cols"], 1, 5, 3)
    rows = c2.slider(t["label_rows"], 1, 12, 8)

    if not st.button("🏷️ " + t["label_generate"]):
        return
    labels = [l.strip() for l in raw.splitlines() if l.strip()]
    if not labels:
        st.warning(t["label_empty"])
        return

    pdf, fam = make_pdf()
    pdf.set_auto_page_break(False)
    margin = 10
    usable_w = pdf.w - 2 * margin
    usable_h = pdf.h - 2 * margin
    cw = usable_w / cols
    ch = usable_h / rows
    per_page = cols * rows

    pdf.set_draw_color(180, 180, 180)
    pdf.set_text_color(20, 20, 20)
    for i, label in enumerate(labels):
        slot = i % per_page
        if slot == 0:
            pdf.add_page()
        r, c = divmod(slot, cols)
        x = margin + c * cw
        y = margin + r * ch
        pdf.rect(x + 1, y + 1, cw - 2, ch - 2)
        pdf.set_xy(x + 3, y + ch / 2 - 4)
        pdf.set_font(fam, "", 11)
        pdf.multi_cell(cw - 6, 5, label, align="C")

    st.download_button("⬇️ " + t["label_download"], pdf_bytes(pdf), file_name="labels.pdf", mime="application/pdf")
