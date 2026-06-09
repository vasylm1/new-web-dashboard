import re

import streamlit as st

from translations import translations


SAMPLE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Preview</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 40px; color: #172033; }
    .card { max-width: 560px; padding: 28px; border: 1px solid #dfe4ee;
            border-radius: 16px; box-shadow: 0 12px 32px #18243d18; }
    h1 { color: #4f46e5; }
  </style>
</head>
<body>
  <main class="card">
    <h1>HTML preview</h1>
    <p>Edit the source to update this isolated preview.</p>
  </main>
</body>
</html>"""

VIEWPORTS = {
    "Responsive": "stretch",
    "Desktop (1200 px)": 1200,
    "Tablet (768 px)": 768,
    "Mobile (390 px)": 390,
}


def _document(source, allow_external):
    policy = (
        "default-src 'none'; img-src data: blob:; style-src 'unsafe-inline'; "
        "font-src data:; media-src data: blob:; frame-src 'none'; form-action 'none'"
    )
    if allow_external:
        policy = (
            "default-src 'none'; img-src data: blob: https: http:; "
            "style-src 'unsafe-inline' https: http:; font-src data: https: http:; "
            "media-src data: blob: https: http:; frame-src 'none'; form-action 'none'"
        )
    guard = (
        f'<meta http-equiv="Content-Security-Policy" content="{policy}">'
        '<base target="_blank">'
    )
    if re.search(r"<head(?:\s[^>]*)?>", source, flags=re.I):
        return re.sub(r"(<head(?:\s[^>]*)?>)", r"\1" + guard, source, count=1, flags=re.I)
    return guard + source


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["htmlview_title"])
    st.caption(t["htmlview_intro"])

    uploaded = st.file_uploader(t["htmlview_upload"], type=["html", "htm"])
    initial = SAMPLE
    if uploaded is not None:
        initial = uploaded.getvalue().decode("utf-8", errors="replace")

    source = st.text_area(t["htmlview_source"], value=initial, height=330)
    controls = st.columns([2, 1, 1])
    viewport = controls[0].selectbox(t["htmlview_viewport"], list(VIEWPORTS))
    height = controls[1].number_input(t["htmlview_height"], 240, 1200, 600, 40)
    allow_external = controls[2].checkbox(t["htmlview_external"], value=False)

    if not source.strip():
        st.info(t["htmlview_empty"])
        return

    if allow_external:
        st.warning(t["htmlview_external_warning"])
    else:
        st.caption(t["htmlview_safe"])

    st.subheader(t["htmlview_preview"])
    st.iframe(_document(source, allow_external), width=VIEWPORTS[viewport], height=height)
    st.download_button(
        "⬇️ " + t["htmlview_download"],
        source,
        file_name="preview.html",
        mime="text/html",
    )
