import io
from PIL import Image, ImageDraw, ImageFilter
import streamlit as st
from translations import translations


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _gradient(size, c1, c2):
    w, h = size
    base = Image.new("RGB", size, c1)
    top = Image.new("RGB", size, c2)
    mask = Image.new("L", size)
    md = mask.load()
    for y in range(h):
        for x in range(w):
            md[x, y] = int(255 * ((x + y) / (w + h)))
    return Image.composite(top, base, mask)


def _round(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["beaut_title"])

    up = st.file_uploader(t["beaut_upload"], type=["png", "jpg", "jpeg", "webp"])
    c1, c2, c3 = st.columns(3)
    padding = c1.slider(t["beaut_padding"], 20, 200, 80)
    radius = c2.slider(t["beaut_radius"], 0, 60, 18)
    shadow = c3.slider(t["beaut_shadow"], 0, 60, 25)
    cc1, cc2 = st.columns(2)
    bg1 = cc1.color_picker(t["beaut_bg1"], "#4361ee")
    bg2 = cc2.color_picker(t["beaut_bg2"], "#a78bfa")

    if not up or not st.button("✨ " + t["beaut_make"]):
        return

    shot = Image.open(up).convert("RGBA")
    shot = _round(shot, radius)
    W, H = shot.width + padding * 2, shot.height + padding * 2
    canvas = _gradient((W, H), _hex(bg1), _hex(bg2)).convert("RGBA")

    if shadow > 0:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([padding, padding + shadow // 2, padding + shot.width, padding + shot.height + shadow // 2],
                             radius=radius, fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(shadow / 2))
        canvas = Image.alpha_composite(canvas, sh)

    canvas.alpha_composite(shot, (padding, padding))
    out = canvas.convert("RGB")
    buf = io.BytesIO()
    out.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["beaut_download"], buf.getvalue(), file_name="beautified.png", mime="image/png")
