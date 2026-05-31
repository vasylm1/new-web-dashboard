import io
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DejaVuSans.ttf",
]


def _font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_caption(draw, text, font, W, y_top):
    """Draw centered uppercase text with a black outline at vertical position y_top."""
    text = text.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2 - bbox[0]
    outline = max(2, font.size // 18)
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            draw.text((x + dx, y_top + dy), text, font=font, fill="black")
    draw.text((x, y_top), text, font=font, fill="white")


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["meme_title"])

    up = st.file_uploader(t["meme_upload"], type=["png", "jpg", "jpeg", "webp"])
    top = st.text_input(t["meme_top"])
    bottom = st.text_input(t["meme_bottom"])

    if not st.button("😂 " + t["meme_make"]):
        return
    if not up or (not top.strip() and not bottom.strip()):
        st.warning(t["meme_empty"])
        return

    img = Image.open(up).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)
    font = _font(max(20, W // 12))

    if top.strip():
        _draw_caption(draw, top, font, W, int(H * 0.03))
    if bottom.strip():
        bbox = draw.textbbox((0, 0), bottom.upper(), font=font)
        _draw_caption(draw, bottom, font, W, H - (bbox[3] - bbox[1]) - int(H * 0.06))

    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["meme_download"], buf.getvalue(), file_name="meme.png", mime="image/png")
