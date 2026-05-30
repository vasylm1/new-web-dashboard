import io
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["road_title"])

    heading = st.text_input(t["road_heading"], placeholder="Product Roadmap 2026")
    items_raw = st.text_area(t["road_items"], height=160, placeholder="Discovery | Q1\nBeta | Q2\nLaunch | Q3")
    primary = st.color_picker(t["primary_color"], "#4361ee")

    if not st.button("🗺️ " + t["road_make"]):
        return

    items = []
    for line in items_raw.splitlines():
        if not line.strip():
            continue
        label, _, date = line.partition("|")
        items.append((label.strip(), date.strip()))
    if not items:
        st.warning(t["road_empty"])
        return

    n = len(items)
    W = max(720, 200 * n + 120)
    H = 380
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    if heading.strip():
        d.text((40, 24), heading, font=_font(28), fill="#111827")

    y = H // 2 + 20
    d.line([(70, y), (W - 70, y)], fill=primary, width=5)
    step = (W - 140) // (n - 1) if n > 1 else 0
    lab_font, date_font = _font(19), _font(15)
    for i, (label, date) in enumerate(items):
        x = 70 + (step * i if n > 1 else (W - 140) // 2)
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=primary)
        above = i % 2 == 0
        ty = y - 78 if above else y + 26
        d.text((x - 80, ty), label[:20], font=lab_font, fill="#111827")
        d.text((x - 80, ty + 24), date, font=date_font, fill="#6b7280")

    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["road_download"], buf.getvalue(), file_name="roadmap.png", mime="image/png")
