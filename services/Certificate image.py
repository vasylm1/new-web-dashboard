import io
import zipfile
import re
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations
from tablutil import read_table, template_bytes, TEMPLATE_MIME

PRIMARY = "#4361ee"
FONTS = {
    "B": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}


def _font(size, bold=False):
    for key in (("B", "") if bold else ("", "B")):
        try:
            return ImageFont.truetype(FONTS[key], size)
        except Exception:
            continue
    return ImageFont.load_default()


def _centered(d, y, text, font, fill, W):
    bbox = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bbox[2] - bbox[0])) / 2, y), text, font=font, fill=fill)


def _make(recipient, text, signer):
    W, H = 1200, 850
    img = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 24, H - 24], outline=PRIMARY, width=6)
    d.rectangle([38, 38, W - 38, H - 38], outline="#d1d5db", width=1)
    _centered(d, 150, "CERTIFICATE", _font(64, True), PRIMARY, W)
    _centered(d, 230, "OF ACHIEVEMENT", _font(26, False), "#6b7280", W)
    _centered(d, 360, recipient, _font(54, True), "#111827", W)
    d.line([(W / 2 - 220, 440), (W / 2 + 220, 440)], fill=PRIMARY, width=2)
    _centered(d, 470, text[:80], _font(24, False), "#4b5563", W)
    if signer.strip():
        _centered(d, 690, signer, _font(22, True), "#111827", W)
        _centered(d, 724, "Signature", _font(16, False), "#9ca3af", W)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["certimg_title"])

    mode_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    mode = mode_map[st.radio(t["batch_mode"], list(mode_map.keys()), horizontal=True)]

    text = st.text_area(t["certimg_text"], value="has successfully completed the course", height=70)
    signer = st.text_input(t["certimg_signer"])

    if mode == "single":
        recipient = st.text_input(t["certimg_recipient"])
        if not st.button("🏅 " + t["certimg_make"]):
            return
        if not recipient.strip():
            st.warning(t["certimg_empty"])
            return
        data = _make(recipient, text, signer)
        st.image(data, use_container_width=True)
        st.download_button("⬇️ " + t["certimg_download"], data, file_name="certificate.png", mime="image/png")
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
    if not st.button("🏅 " + t["batch_generate"]):
        return

    names = [str(v).strip() for v in df[col].dropna() if str(v).strip()]
    if not names:
        st.warning(t["batch_empty"])
        return
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            safe = re.sub(r"[^\w-]+", "_", name)[:40] or "certificate"
            zf.writestr(f"{safe}.png", _make(name, text, signer))
    st.success(f"{t['batch_done']}: {len(names)}")
    st.download_button("⬇️ " + t["batch_zip"], zip_buf.getvalue(), file_name="certificates.zip", mime="application/zip")
