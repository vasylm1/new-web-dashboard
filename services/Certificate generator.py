import io
import streamlit as st
from PIL import Image
from translations import translations
from pdfutil import make_pdf, pdf_bytes
from tablutil import read_table, template_bytes, TEMPLATE_MIME

STYLES = {
    "classic": dict(accent=(67, 97, 238), border="double", title=(67, 97, 238), name=(20, 20, 20), sub=(90, 90, 90)),
    "modern":  dict(accent=(15, 118, 110), border="bar", title=(15, 118, 110), name=(15, 23, 42), sub=(100, 116, 139)),
    "elegant": dict(accent=(184, 134, 11), border="ornate", title=(184, 134, 11), name=(63, 45, 16), sub=(138, 122, 85)),
    "minimal": dict(accent=(17, 24, 39), border="thin", title=(17, 24, 39), name=(17, 24, 39), sub=(156, 163, 175)),
}


def _draw(pdf, fam, recipient, text, signer, cdate, style, logo):
    s = STYLES.get(style, STYLES["classic"])
    a = s["accent"]
    pdf.add_page()
    W, H = pdf.w, pdf.h
    pdf.set_draw_color(*a)
    if s["border"] == "double":
        pdf.set_line_width(2); pdf.rect(10, 10, W - 20, H - 20)
        pdf.set_draw_color(200, 200, 200); pdf.set_line_width(0.4); pdf.rect(15, 15, W - 30, H - 30)
    elif s["border"] == "bar":
        pdf.set_fill_color(*a); pdf.rect(10, 10, 8, H - 20, style="F")
        pdf.set_draw_color(220, 220, 220); pdf.set_line_width(0.5); pdf.rect(24, 15, W - 34, H - 30)
    elif s["border"] == "ornate":
        pdf.set_line_width(1.6); pdf.rect(10, 10, W - 20, H - 20)
        pdf.set_line_width(0.4); pdf.rect(14, 14, W - 28, H - 28)
        pdf.set_fill_color(*a)
        for cx, cy in [(14, 14), (W - 14, 14), (14, H - 14), (W - 14, H - 14)]:
            pdf.ellipse(cx - 2, cy - 2, 4, 4, style="F")
    else:  # thin
        pdf.set_line_width(0.8); pdf.rect(14, 14, W - 28, H - 28)

    y = 30
    if logo:
        try:
            im = Image.open(io.BytesIO(logo))
            aspect = im.width / im.height
        except Exception:
            aspect = 1.0
        lw = 20 * aspect
        pdf.image(io.BytesIO(logo), x=(W - lw) / 2, y=16, h=20)
        y = 44

    pdf.set_y(y)
    pdf.set_text_color(*s["title"]); pdf.set_font(fam, "B", 34)
    pdf.cell(0, 16, "Certificate", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*s["sub"]); pdf.set_font(fam, "", 13)
    pdf.cell(0, 9, "of Achievement", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_text_color(*s["name"]); pdf.set_font(fam, "B", 26)
    pdf.cell(0, 14, recipient, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3); pdf.set_font(fam, "", 13); pdf.set_text_color(*s["sub"])
    pdf.multi_cell(0, 8, text, align="C")
    pdf.ln(16); pdf.set_font(fam, "", 12)
    line = "  |  ".join(filter(None, [signer.strip(), cdate.strip()]))
    if line:
        pdf.cell(0, 8, line, align="C", new_x="LMARGIN", new_y="NEXT")


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["cert_title"])

    mode_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    mode = mode_map[st.radio(t["batch_mode"], list(mode_map.keys()), horizontal=True)]

    style_map = {t["cert_style_classic"]: "classic", t["cert_style_modern"]: "modern",
                 t["cert_style_elegant"]: "elegant", t["cert_style_minimal"]: "minimal"}
    style = style_map[st.selectbox(t["cert_style"], list(style_map.keys()))]
    text = st.text_area(t["cert_text"], value="has successfully completed the course", height=70)
    signer = st.text_input(t["cert_signer"])
    cdate = st.text_input(t["cert_date"])
    logo_file = st.file_uploader(t["cert_logo"], type=["png", "jpg", "jpeg"])
    logo = logo_file.getvalue() if logo_file else None

    if mode == "single":
        recipient = st.text_input(t["cert_recipient"])
        if not st.button("🏆 " + t["cert_generate"]):
            return
        if not recipient.strip():
            st.warning(t["cert_empty"])
            return
        pdf, fam = make_pdf(orientation="L")
        _draw(pdf, fam, recipient, text, signer, cdate, style, logo)
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
        _draw(pdf, fam, name, text, signer, cdate, style, logo)
    st.success(f"{t['batch_done']}: {len(names)}")
    st.download_button("⬇️ " + t["cert_download"], pdf_bytes(pdf), file_name="certificates.pdf", mime="application/pdf")
