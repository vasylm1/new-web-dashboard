import io
import zipfile
from PIL import Image, ImageOps
import streamlit as st
from translations import translations


def _crop(img, size, mode, bg):
    img = img.convert("RGB")
    if mode == "cover":
        out = ImageOps.fit(img, size, Image.LANCZOS)
    else:
        out = Image.new("RGB", size, bg)
        fitted = img.copy()
        fitted.thumbnail(size, Image.LANCZOS)
        out.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return buf.getvalue()

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

    batch_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    batch = batch_map[st.radio(t["batch_mode"], list(batch_map.keys()), horizontal=True)]

    preset = st.selectbox(t["crop_preset"], list(PRESETS.keys()))
    mode_map = {t["crop_cover"]: "cover", t["crop_contain"]: "contain"}
    mode = mode_map[st.radio(t["crop_mode"], list(mode_map.keys()), horizontal=True)]
    bg = st.color_picker(t["crop_bg"], "#ffffff") if mode == "contain" else "#ffffff"
    size = PRESETS[preset]

    if batch == "batch":
        files = st.file_uploader(t["batch_files_upload"], type=["png", "jpg", "jpeg", "webp", "bmp"],
                                 accept_multiple_files=True)
        if not files or not st.button("✂️ " + t["crop_make"]):
            return
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, f in enumerate(files):
                try:
                    img = Image.open(f)
                except Exception:
                    continue
                stem = f.name.rsplit(".", 1)[0] or f"image_{i + 1}"
                zf.writestr(f"{stem}.png", _crop(img, size, mode, bg))
        st.success(f"{t['batch_done']}: {len(files)}")
        st.download_button("⬇️ " + t["batch_zip"], zip_buf.getvalue(), file_name="cropped.zip", mime="application/zip")
        return

    up = st.file_uploader(t["crop_upload"], type=["png", "jpg", "jpeg", "webp", "bmp"])
    if not up or not st.button("✂️ " + t["crop_make"]):
        return
    data = _crop(Image.open(up), size, mode, bg)
    st.image(data, use_container_width=True)
    st.download_button("⬇️ " + t["crop_download"], data, file_name="cropped.png", mime="image/png")
