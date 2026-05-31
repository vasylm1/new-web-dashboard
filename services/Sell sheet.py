import html
import streamlit as st
import streamlit.components.v1 as components
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["sell_title"])

    left, right = st.columns(2, gap="large")
    with left:
        product = st.text_input(t["sell_product"], placeholder="Acme Analytics")
        tagline = st.text_input(t["sell_tagline"])
        overview = st.text_area(t["sell_overview"], height=100)
        features = st.text_area(t["sell_features"], height=100, placeholder="Real-time dashboards\nNo-code setup")
        benefits = st.text_area(t["sell_benefits"], height=100)
        cta = st.text_input(t["sell_cta"])
        primary = st.color_picker(t["primary_color"], "#4361ee")

    if not product.strip():
        st.info(t["sell_empty"])
        return

    e = lambda v: html.escape(v or "")
    li = lambda txt: "".join(f"<li style='margin:4px 0;'>{e(l)}</li>" for l in txt.splitlines() if l.strip())

    doc = f"""<!doctype html><html><head><meta charset='utf-8'></head>
<body style='margin:0;font-family:Segoe UI,Arial,sans-serif;color:#1f2937;'>
<div style='max-width:680px;margin:auto;padding:24px;'>
<div style='border-left:6px solid {primary};padding-left:16px;margin-bottom:20px;'>
<h1 style='margin:0;font-size:30px;color:#111827;'>{e(product)}</h1>
<div style='color:{primary};font-weight:600;font-size:16px;'>{e(tagline)}</div></div>
<p style='font-size:15px;line-height:1.6;'>{e(overview)}</p>
<div style='display:flex;gap:24px;flex-wrap:wrap;'>
<div style='flex:1;min-width:240px;'><h3 style='color:{primary};'>★ {e(t["sell_features"])}</h3><ul style='padding-left:18px;'>{li(features)}</ul></div>
<div style='flex:1;min-width:240px;'><h3 style='color:{primary};'>✓ {e(t["sell_benefits"])}</h3><ul style='padding-left:18px;'>{li(benefits)}</ul></div>
</div>
<div style='margin-top:24px;background:{primary};color:#fff;padding:16px 20px;border-radius:10px;font-weight:600;text-align:center;'>{e(cta)}</div>
</div></body></html>"""

    with right:
        st.subheader(t["preview"])
        components.html(doc, height=560, scrolling=True)
        st.download_button("⬇️ " + t["sell_download"], doc, file_name="sell_sheet.html", mime="text/html")
