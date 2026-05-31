import io
from PIL import Image, ImageDraw
import streamlit as st
from translations import translations


def _phone(shot):
    # Fit screenshot into a 9:19.5 screen with rounded bezel + notch.
    sw, sh = 360, 780
    screen = shot.convert("RGB").resize((sw, sh))
    pad = 18
    W, H = sw + pad * 2, sh + pad * 2
    body = Image.new("RGB", (W, H), "#111827")
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=48, fill="#111827")
    body.paste(screen, (pad, pad))
    # rounded screen mask
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([pad, pad, pad + sw, pad + sh], radius=30, fill=255)
    final = Image.new("RGB", (W, H), "#111827")
    final.paste(body, (0, 0))
    final.paste(screen, (pad, pad), mask.crop((pad, pad, pad + sw, pad + sh)).resize((sw, sh)))
    d2 = ImageDraw.Draw(final)
    d2.rounded_rectangle([W // 2 - 45, pad + 6, W // 2 + 45, pad + 24], radius=10, fill="#111827")
    return final


def _laptop(shot):
    sw, sh = 800, 500
    screen = shot.convert("RGB").resize((sw, sh))
    bezel = 16
    W = sw + bezel * 2
    H = sh + bezel * 2 + 24
    body = Image.new("RGB", (W, H), "#1f2937")
    body.paste(screen, (bezel, bezel))
    d = ImageDraw.Draw(body)
    d.rectangle([0, H - 24, W, H], fill="#9ca3af")
    d.rounded_rectangle([W // 2 - 60, H - 16, W // 2 + 60, H - 8], radius=6, fill="#6b7280")
    base = Image.new("RGB", (W + 120, H + 20), "#ffffff")
    base.paste(body, (60, 10))
    return base


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["dev_title"])

    up = st.file_uploader(t["dev_upload"], type=["png", "jpg", "jpeg", "webp"])
    dev_map = {t["dev_phone"]: "phone", t["dev_laptop"]: "laptop"}
    device = dev_map[st.radio(t["dev_device"], list(dev_map.keys()), horizontal=True)]

    if not up or not st.button("📱 " + t["dev_make"]):
        return

    shot = Image.open(up)
    out = _phone(shot) if device == "phone" else _laptop(shot)
    buf = io.BytesIO()
    out.save(buf, "PNG")
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["dev_download"], buf.getvalue(), file_name="device_mockup.png", mime="image/png")
