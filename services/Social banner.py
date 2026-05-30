import io
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations

PRESETS = {
    "LinkedIn Banner (1584×396)": (1584, 396),
    "X Header (1500×500)": (1500, 500),
    "Facebook Cover (820×312)": (820, 312),
    "YouTube Banner (2048×1152)": (2048, 1152),
}
FONT_PATHS = {
    "B": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}


def _font(size, bold=True):
    for key in (("B", "") if bold else ("", "B")):
        try:
            return ImageFont.truetype(FONT_PATHS[key], size)
        except Exception:
            continue
    return ImageFont.load_default()


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _gradient(size, c1, c2):
    w, h = size
    base, top = Image.new("RGB", size, c1), Image.new("RGB", size, c2)
    mask = Image.new("L", size)
    px = mask.load()
    for x in range(w):
        v = int(255 * x / max(1, w - 1))
        for y in range(h):
            px[x, y] = v
    return Image.composite(top, base, mask)


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["sb_title"])

    preset = st.selectbox(t["sb_preset"], list(PRESETS.keys()))
    name = st.text_input(t["sb_name"], placeholder="Vasyl Madei")
    tagline = st.text_input(t["sb_tagline"], placeholder="Product Marketing · Data · Automation")
    c1, c2 = st.columns(2)
    bg1 = c1.color_picker(t["sb_bg1"], "#3f37c9")
    bg2 = c2.color_picker(t["sb_bg2"], "#4895ef")

    if not st.button("🎯 " + t["sb_make"]):
        return

    size = PRESETS[preset]
    img = _gradient(size, _hex(bg1), _hex(bg2))
    d = ImageDraw.Draw(img)
    W, H = size
    d.text((60, H // 2 - 40), name, font=_font(max(28, H // 8), True), fill="#ffffff")
    if tagline.strip():
        d.text((62, H // 2 + 24), tagline, font=_font(max(16, H // 16), False), fill=(255, 255, 255, 220))

    buf = io.BytesIO()
    img.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["sb_download"], buf.getvalue(), file_name="banner.png", mime="image/png")
