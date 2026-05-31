import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from translations import translations

# Position label (language-neutral arrows) -> (fx, fy) anchor fractions.
POSITIONS = {"↖": (0, 0), "↗": (1, 0), "●": (0.5, 0.5), "↙": (0, 1), "↘": (1, 1)}

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


def _anchor(outer, inner, fx, fy, margin):
    x = int((outer[0] - inner[0]) * fx)
    y = int((outer[1] - inner[1]) * fy)
    # keep a small margin from the edges
    x = min(max(x, margin), max(margin, outer[0] - inner[0] - margin)) if fx in (0, 1) else x
    y = min(max(y, margin), max(margin, outer[1] - inner[1] - margin)) if fy in (0, 1) else y
    return x, y


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["wm_title"])

    batch_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    batch = batch_map[st.radio(t["batch_mode"], list(batch_map.keys()), horizontal=True)]

    text = st.text_input(t["wm_text"])
    logo = st.file_uploader(t["wm_logo"], type=["png"])
    c1, c2, c3 = st.columns(3)
    pos = c1.selectbox(t["wm_position"], list(POSITIONS.keys()), index=4)
    opacity = c2.slider(t["wm_opacity"], 10, 100, 50)
    size = c3.slider(t["wm_size"], 5, 50, 20)
    logo_img = Image.open(logo).convert("RGBA") if logo else None

    if batch == "batch":
        files = st.file_uploader(t["batch_files_upload"], type=["png", "jpg", "jpeg", "webp"],
                                 accept_multiple_files=True)
        if not files or not st.button("💧 " + t["wm_apply"]):
            return
        if not text.strip() and logo_img is None:
            st.warning(t["wm_empty"])
            return
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, f in enumerate(files):
                try:
                    base = Image.open(f).convert("RGBA")
                except Exception:
                    continue
                stem = f.name.rsplit(".", 1)[0] or f"image_{i + 1}"
                zf.writestr(f"{stem}.png", _apply(base, text, logo_img, pos, opacity, size))
        st.success(f"{t['batch_done']}: {len(files)}")
        st.download_button("⬇️ " + t["batch_zip"], zip_buf.getvalue(), file_name="watermarked.zip", mime="application/zip")
        return

    up = st.file_uploader(t["wm_upload"], type=["png", "jpg", "jpeg", "webp"])
    if not st.button("💧 " + t["wm_apply"]):
        return
    if not up or (not text.strip() and logo_img is None):
        st.warning(t["wm_empty"])
        return
    data = _apply(Image.open(up).convert("RGBA"), text, logo_img, pos, opacity, size)
    st.image(data, use_container_width=True)
    st.download_button("⬇️ " + t["wm_download"], data, file_name="watermarked.png", mime="image/png")


def _apply(base, text, logo_img, pos, opacity, size):
    W, H = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fx, fy = POSITIONS[pos]
    margin = int(min(W, H) * 0.03)
    if logo_img is not None:
        lg = logo_img.copy()
        target_w = max(1, int(W * size / 100))
        ratio = target_w / lg.width
        lg = lg.resize((target_w, max(1, int(lg.height * ratio))), Image.LANCZOS)
        alpha = lg.split()[3].point(lambda v: int(v * opacity / 100))
        lg.putalpha(alpha)
        overlay.alpha_composite(lg, _anchor((W, H), lg.size, fx, fy, margin))
    else:
        draw = ImageDraw.Draw(overlay)
        font = _font(max(12, int(H * size / 100)))
        bbox = draw.textbbox((0, 0), text, font=font)
        x, y = _anchor((W, H), (bbox[2] - bbox[0], bbox[3] - bbox[1]), fx, fy, margin)
        draw.text((x - bbox[0], y - bbox[1]), text, font=font, fill=(255, 255, 255, int(255 * opacity / 100)))
    out = Image.alpha_composite(base, overlay).convert("RGB")
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return buf.getvalue()
