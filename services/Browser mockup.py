import io
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations

FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
BAR = 44


def _font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["brow_title"])

    up = st.file_uploader(t["brow_upload"], type=["png", "jpg", "jpeg", "webp"])
    url = st.text_input(t["brow_url"], value="example.com")

    if not up or not st.button("🌐 " + t["brow_make"]):
        return

    shot = Image.open(up).convert("RGB")
    W = shot.width
    canvas = Image.new("RGB", (W, shot.height + BAR), "#e5e7eb")
    d = ImageDraw.Draw(canvas)

    # chrome bar with traffic lights and an address pill
    d.rectangle([0, 0, W, BAR], fill="#e5e7eb")
    for i, col in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
        cx = 18 + i * 20
        d.ellipse([cx, BAR // 2 - 6, cx + 12, BAR // 2 + 6], fill=col)
    d.rounded_rectangle([90, 9, W - 16, BAR - 9], radius=12, fill="#ffffff")
    d.text((104, BAR // 2 - 8), url[:80], font=_font(15), fill="#6b7280")

    canvas.paste(shot, (0, BAR))
    buf = io.BytesIO()
    canvas.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["brow_download"], buf.getvalue(), file_name="browser_mockup.png", mime="image/png")
