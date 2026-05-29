import streamlit as st
import io
from PIL import Image
from gtts import gTTS
from PyPDF2 import PdfReader
from translations import translations

# 📁 Universal File Converter UI and logic

# gTTS rejects very large inputs and gets slow; cap to keep the app responsive.
MAX_TTS_CHARS = 20000

IMAGE_EXTS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff"}

# Map the human-readable conversion choice to (allowed input exts, target format)
IMAGE_CONVERSIONS = {
    "Image: PNG to JPG": ("JPEG", "jpg"),
    "Image: JPG to PNG": ("PNG", "png"),
    "Image: WEBP to PNG": ("PNG", "png"),
    "Image: BMP to PNG": ("PNG", "png"),
    "Image: TIFF to PNG": ("PNG", "png"),
}


def convert_image(uploaded_file, pil_format):
    """Convert an uploaded image to the target format, returning PNG/JPEG bytes."""
    image = Image.open(uploaded_file)
    # JPEG has no alpha channel; flatten transparency onto white.
    if pil_format == "JPEG" and image.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        rgba = image.convert("RGBA")
        background.paste(rgba, mask=rgba.split()[-1])
        image = background
    buf = io.BytesIO()
    image.save(buf, format=pil_format)
    return buf.getvalue()


def pdf_to_mp3(uploaded_file, lang_code):
    """Extract PDF text and synthesize speech, returning MP3 bytes."""
    reader = PdfReader(uploaded_file)
    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        return None, "no_text"
    truncated = len(text) > MAX_TTS_CHARS
    if truncated:
        text = text[:MAX_TTS_CHARS]
    tts = gTTS(text=text, lang=lang_code)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue(), ("truncated" if truncated else None)


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["fileconv_title"])

    # 🕽 File uploader
    uploaded_file = st.file_uploader(
        t["fileconv_upload"], type=["pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff"]
    )

    # 🗂 Format selector
    conversion_type = st.selectbox(
        t["fileconv_conversion_type"],
        list(IMAGE_CONVERSIONS.keys()) + ["PDF to MP3"],
    )

    lang_code = None
    if conversion_type == "PDF to MP3":
        lang_code = st.selectbox(
            t["fileconv_language"], ["en", "pl", "uk", "de", "es", "fr", "zh-cn"]
        )

    if not (uploaded_file and st.button(t["fileconv_convert_button"])):
        return

    ext = uploaded_file.name.lower().rsplit(".", 1)[-1]

    # Guard against a mismatch between the uploaded file and the chosen conversion.
    if conversion_type == "PDF to MP3" and ext != "pdf":
        st.error(t["fileconv_mismatch"])
        return
    if conversion_type in IMAGE_CONVERSIONS and ext not in IMAGE_EXTS:
        st.error(t["fileconv_mismatch"])
        return

    with st.spinner(t["fileconv_spinner"]):
        try:
            if conversion_type in IMAGE_CONVERSIONS:
                pil_format, out_ext = IMAGE_CONVERSIONS[conversion_type]
                data = convert_image(uploaded_file, pil_format)
                st.success(t["fileconv_success"])
                st.download_button(
                    t["fileconv_download_image"], data, file_name=f"converted.{out_ext}"
                )
            else:  # PDF to MP3
                data, note = pdf_to_mp3(uploaded_file, lang_code)
                if note == "no_text":
                    st.error(t["fileconv_no_text"])
                    return
                if note == "truncated":
                    st.warning(t["fileconv_truncated"])
                st.success(t["fileconv_mp3_success"])
                st.download_button(
                    t["fileconv_download_mp3"], data, file_name="output.mp3"
                )
        except Exception as e:
            st.error(f"{t['fileconv_error']} {e}")
