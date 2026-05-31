from PIL import Image
import streamlit as st
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["palette_title"])

    up = st.file_uploader(t["palette_upload"], type=["png", "jpg", "jpeg", "webp", "bmp"])
    n = st.slider(t["palette_count"], 3, 10, 6)
    if not up:
        return

    try:
        img = Image.open(up).convert("RGB")
    except Exception as e:
        st.error(f"{t['palette_error']} {e}")
        return

    if not st.button("🎨 " + t["palette_extract"]):
        return

    small = img.copy()
    small.thumbnail((200, 200))
    quant = small.quantize(colors=n, method=Image.MEDIANCUT)
    palette = quant.getpalette()
    # getcolors() -> list of (count, palette_index); sort by frequency desc.
    counts = sorted(quant.getcolors() or [], reverse=True)[:n]

    st.subheader(t["palette_result"])
    cols = st.columns(len(counts) or 1)
    css_lines = []
    for i, (_, idx) in enumerate(counts):
        r, g, b = palette[idx * 3:idx * 3 + 3]
        hex_code = f"#{r:02X}{g:02X}{b:02X}"
        with cols[i]:
            st.markdown(
                f"<div style='background:{hex_code};height:64px;border-radius:8px;border:1px solid #ddd'></div>",
                unsafe_allow_html=True,
            )
            st.caption(hex_code)
        css_lines.append(f"  --color-{i + 1}: {hex_code};")

    css = ":root {\n" + "\n".join(css_lines) + "\n}\n"
    st.code(css, language="css")
    st.download_button("⬇️ " + t["palette_download"], css, file_name="palette.css", mime="text/css")
