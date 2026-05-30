import io
from PIL import Image, ImageOps
import streamlit as st
from translations import translations

# Preset name (with dimensions) -> (width, height). Names are platform proper nouns.
PRESETS = {
    "Instagram Square (1080×1080)": (1080, 1080),
    "Instagram Portrait (1080×1350)": (1080, 1350),
    "Instagram Story (1080×1920)": (1080, 1920),
    "Facebook Cover (820×312)": (820, 312),
    "LinkedIn Banner (1584×396)": (1584, 396),
    "X Header (1500×500)": (1500, 500),
}


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["crop_title"])

    up = st.file_uploader(t["crop_upload"], type=["png", "jpg", "jpeg", "webp", "bmp"])
    if not up:
        return

    preset = st.selectbox(t["crop_preset"], list(PRESETS.keys()))
    mode_map = {t["crop_cover"]: "cover", t["crop_contain"]: "contain"}
    mode = mode_map[st.radio(t["crop_mode"], list(mode_map.keys()), horizontal=True)]
    bg = st.color_picker(t["crop_bg"], "#ffffff") if mode == "contain" else "#ffffff"

    if not st.button("✂️ " + t["crop_make"]):
        return

    img = Image.open(up).convert("RGB")
    size = PRESETS[preset]
    if mode == "cover":
        out = ImageOps.fit(img, size, Image.LANCZOS)
    else:
        canvas = Image.new("RGB", size, bg)
        fitted = img.copy()
        fitted.thumbnail(size, Image.LANCZOS)
        canvas.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
        out = canvas

    buf = io.BytesIO()
    out.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["crop_download"], buf.getvalue(), file_name="cropped.png", mime="image/png")
