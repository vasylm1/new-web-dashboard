import io
import zipfile
import re
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations
from tablutil import read_table, template_bytes, TEMPLATE_MIME

FONTS = {
    "B": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "S": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "SB": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
}

# Each style: accent color, background, name color, sub color, border kind, serif flag.
STYLES = {
    "classic": dict(accent="#4361ee", bg="#ffffff", name="#111827", sub="#6b7280", border="double", serif=False),
    "modern":  dict(accent="#0f766e", bg="#ffffff", name="#0f172a", sub="#64748b", border="bar", serif=False),
    "elegant": dict(accent="#b8860b", bg="#fffdf6", name="#3f2d10", sub="#8a7a55", border="ornate", serif=True),
    "minimal": dict(accent="#111827", bg="#ffffff", name="#111827", sub="#9ca3af", border="thin", serif=False),
}


def _font(size, bold=False, serif=False):
    keys = (("SB", "S", "B", "") if bold else ("S", "SB", "", "B")) if serif else (("B", "") if bold else ("", "B"))
    for k in keys:
        try:
            return ImageFont.truetype(FONTS[k], size)
        except Exception:
            continue
    return ImageFont.load_default()


def _centered(d, y, text, font, fill, W):
    bbox = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bbox[2] - bbox[0])) / 2, y), text, font=font, fill=fill)


def _border(d, s, W, H):
    a = s["accent"]
    if s["border"] == "double":
        d.rectangle([24, 24, W - 24, H - 24], outline=a, width=6)
        d.rectangle([40, 40, W - 40, H - 40], outline="#d1d5db", width=1)
    elif s["border"] == "bar":
        d.rectangle([0, 0, 26, H], fill=a)
        d.rectangle([46, 30, W - 30, H - 30], outline="#e5e7eb", width=2)
    elif s["border"] == "ornate":
        d.rectangle([22, 22, W - 22, H - 22], outline=a, width=5)
        d.rectangle([34, 34, W - 34, H - 34], outline=a, width=1)
        for cx, cy in [(34, 34), (W - 34, 34), (34, H - 34), (W - 34, H - 34)]:
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=a)
    else:  # thin
        d.rectangle([40, 40, W - 40, H - 40], outline=a, width=2)


def make_certificate(recipient, text, signer, style_key, logo_img):
    s = STYLES.get(style_key, STYLES["classic"])
    serif = s["serif"]
    W, H = 1200, 850
    img = Image.new("RGB", (W, H), s["bg"])
    d = ImageDraw.Draw(img)
    _border(d, s, W, H)

    y = 120
    if logo_img is not None:
        logo = logo_img.convert("RGBA")
        lw = int(logo.width * (90 / logo.height))
        logo = logo.resize((max(1, lw), 90), Image.LANCZOS)
        img.paste(logo, ((W - logo.width) // 2, 70), logo)
        y = 190

    _centered(d, y, "CERTIFICATE", _font(60, True, serif), s["accent"], W)
    _centered(d, y + 78, "OF ACHIEVEMENT", _font(24, False, serif), s["sub"], W)
    _centered(d, y + 190, recipient, _font(52, True, serif), s["name"], W)
    d.line([(W / 2 - 220, y + 270), (W / 2 + 220, y + 270)], fill=s["accent"], width=2)
    _centered(d, y + 300, text[:80], _font(23, False, serif), s["sub"], W)
    if signer.strip():
        _centered(d, H - 150, signer, _font(22, True, serif), s["name"], W)
        d.line([(W / 2 - 140, H - 120), (W / 2 + 140, H - 120)], fill="#d1d5db", width=1)
        _centered(d, H - 112, "Signature", _font(15, False, serif), s["sub"], W)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["certimg_title"])

    mode_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    mode = mode_map[st.radio(t["batch_mode"], list(mode_map.keys()), horizontal=True)]

    style_map = {t["cert_style_classic"]: "classic", t["cert_style_modern"]: "modern",
                 t["cert_style_elegant"]: "elegant", t["cert_style_minimal"]: "minimal"}
    style_key = style_map[st.selectbox(t["cert_style"], list(style_map.keys()))]
    text = st.text_area(t["certimg_text"], value="has successfully completed the course", height=70)
    signer = st.text_input(t["certimg_signer"])
    logo_file = st.file_uploader(t["cert_logo"], type=["png", "jpg", "jpeg"])
    logo_img = Image.open(logo_file) if logo_file else None

    if mode == "single":
        recipient = st.text_input(t["certimg_recipient"])
        if not st.button("🏅 " + t["certimg_make"]):
            return
        if not recipient.strip():
            st.warning(t["certimg_empty"])
            return
        data = make_certificate(recipient, text, signer, style_key, logo_img)
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
            zf.writestr(f"{safe}.png", make_certificate(name, text, signer, style_key, logo_img))
    st.success(f"{t['batch_done']}: {len(names)}")
    st.download_button("⬇️ " + t["batch_zip"], zip_buf.getvalue(), file_name="certificates.zip", mime="application/zip")
