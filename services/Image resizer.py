import io
import zipfile
import streamlit as st
from PIL import Image
from translations import translations

FAVICON_SIZES = [16, 32, 48, 180, 192]
EXT = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}


def _crop_square(img):
    """Center-crop to a square so favicons aren't distorted."""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def _encode(img, fmt, quality):
    """Encode a PIL image to bytes in the given format."""
    buf = io.BytesIO()
    if fmt == "JPEG":
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
            img = bg
        img.save(buf, format="JPEG", quality=quality, optimize=True)
    elif fmt == "WEBP":
        img.save(buf, format="WEBP", quality=quality, method=6)
    else:  # PNG
        img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _make_favicon_pack(img):
    base = _crop_square(img.convert("RGBA"))
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for size in FAVICON_SIZES:
            resized = base.resize((size, size), Image.LANCZOS)
            out = io.BytesIO()
            resized.save(out, format="PNG", optimize=True)
            zf.writestr(f"favicon-{size}x{size}.png", out.getvalue())
        # A classic multi-resolution .ico as well.
        ico = io.BytesIO()
        base.resize((64, 64), Image.LANCZOS).save(
            ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
        )
        zf.writestr("favicon.ico", ico.getvalue())
    return zip_buf.getvalue()


def _kb(n_bytes):
    return f"{max(1, round(n_bytes / 1024))} KB"


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["imgresize_title"])

    batch_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    batch = batch_map[st.radio(t["batch_mode"], list(batch_map.keys()), horizontal=True)]

    if batch == "batch":
        _run_batch(t)
        return

    uploaded = st.file_uploader(
        t["imgresize_upload"], type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"]
    )
    if not uploaded:
        return

    try:
        img = Image.open(uploaded)
        img.load()
    except Exception as e:
        st.error(f"{t['imgresize_error']} {e}")
        return

    orig_bytes = uploaded.getvalue()
    col1, col2 = st.columns(2)
    with col1:
        st.image(orig_bytes, caption=f"{t['imgresize_original']} · {_kb(len(orig_bytes))} · {img.size[0]}×{img.size[1]}", use_container_width=True)

    mode = st.radio(
        t["imgresize_mode"],
        [t["imgresize_mode_resize"], t["imgresize_mode_favicon"]],
        horizontal=True,
    )

    # --- Favicon pack mode ---
    if mode == t["imgresize_mode_favicon"]:
        st.info(t["imgresize_favicon_info"])
        if st.button("⚙️ " + t["imgresize_process"]):
            zip_bytes = _make_favicon_pack(img)
            st.success(t["imgresize_success"])
            st.download_button(
                "⬇️ " + t["imgresize_download_zip"],
                data=zip_bytes,
                file_name="favicons.zip",
                mime="application/zip",
                use_container_width=True,
            )
        return

    # --- Resize & compress mode ---
    fmt = st.selectbox(t["imgresize_format"], ["PNG", "JPEG", "WEBP"])
    max_dim = st.slider(t["imgresize_max_dim"], 0, 4000, 0, step=50)
    quality = st.slider(t["imgresize_quality"], 10, 100, 85, disabled=(fmt == "PNG"))

    if st.button("⚙️ " + t["imgresize_process"]):
        work = img.copy()
        if max_dim > 0:
            work.thumbnail((max_dim, max_dim), Image.LANCZOS)
        out_bytes = _encode(work, fmt, quality)

        with col2:
            st.image(out_bytes, caption=f"{t['imgresize_result']} · {_kb(len(out_bytes))} · {work.size[0]}×{work.size[1]}", use_container_width=True)

        saved = 1 - (len(out_bytes) / len(orig_bytes)) if orig_bytes else 0
        if saved > 0:
            st.success(f"{t['imgresize_saved']}: {round(saved * 100)}%  ({_kb(len(orig_bytes))} → {_kb(len(out_bytes))})")
        st.download_button(
            "⬇️ " + t["imgresize_download"],
            data=out_bytes,
            file_name=f"image.{EXT[fmt]}",
            mime=f"image/{EXT[fmt].replace('jpg', 'jpeg')}",
            use_container_width=True,
        )


def _run_batch(t):
    files = st.file_uploader(
        t["batch_files_upload"], type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
    )
    fmt = st.selectbox(t["imgresize_format"], ["PNG", "JPEG", "WEBP"])
    max_dim = st.slider(t["imgresize_max_dim"], 0, 4000, 0, step=50)
    quality = st.slider(t["imgresize_quality"], 10, 100, 85, disabled=(fmt == "PNG"))

    if not files or not st.button("⚙️ " + t["imgresize_process"]):
        return

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, f in enumerate(files):
            try:
                img = Image.open(f)
                img.load()
            except Exception:
                continue
            if max_dim > 0:
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)
            stem = f.name.rsplit(".", 1)[0] or f"image_{i + 1}"
            zf.writestr(f"{stem}.{EXT[fmt]}", _encode(img, fmt, quality))
    st.success(f"{t['batch_done']}: {len(files)}")
    st.download_button("⬇️ " + t["batch_zip"], zip_buf.getvalue(), file_name="images.zip", mime="application/zip")
