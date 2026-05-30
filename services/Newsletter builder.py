import html
import streamlit as st
import streamlit.components.v1 as components
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["news_title"])

    left, right = st.columns(2, gap="large")
    with left:
        brand = st.text_input(t["news_brand"], placeholder="Acme")
        headline = st.text_input(t["news_headline"])
        intro = st.text_area(t["news_intro"], height=80)
        body = st.text_area(t["news_body"], height=160)
        cta_text = st.text_input(t["news_cta_text"], placeholder="Read more")
        cta_url = st.text_input(t["news_cta_url"], placeholder="https://...")
        footer = st.text_input(t["news_footer"], placeholder="© Acme · Unsubscribe")
        primary = st.color_picker(t["primary_color"], "#4361ee")

    e = lambda v: html.escape(v or "")
    paras = lambda txt: "".join(
        f"<p style='margin:0 0 14px;'>{e(line)}</p>" for line in txt.splitlines() if line.strip()
    )
    button = ""
    if cta_text.strip():
        button = (f"<a href='{e(cta_url)}' style='display:inline-block;background:{primary};color:#fff;"
                  f"text-decoration:none;padding:12px 24px;border-radius:8px;font-weight:600;'>{e(cta_text)}</a>")

    doc = f"""<!doctype html><html><head><meta charset='utf-8'></head>
<body style='margin:0;background:#f3f4f6;font-family:Arial,Helvetica,sans-serif;'>
<table width='100%' cellpadding='0' cellspacing='0'><tr><td align='center' style='padding:24px;'>
<table width='600' cellpadding='0' cellspacing='0' style='background:#fff;border-radius:12px;overflow:hidden;'>
<tr><td style='background:{primary};color:#fff;padding:18px 28px;font-size:18px;font-weight:700;'>{e(brand) or "Newsletter"}</td></tr>
<tr><td style='padding:28px;color:#1f2937;'>
<h1 style='margin:0 0 12px;font-size:24px;color:#111827;'>{e(headline)}</h1>
<div style='color:#6b7280;font-size:15px;'>{paras(intro)}</div>
<div style='font-size:15px;line-height:1.6;'>{paras(body)}</div>
<div style='margin:22px 0;'>{button}</div>
</td></tr>
<tr><td style='padding:18px 28px;background:#f9fafb;color:#9ca3af;font-size:12px;'>{e(footer)}</td></tr>
</table></td></tr></table></body></html>"""

    with right:
        st.subheader(t["preview"])
        components.html(doc, height=560, scrolling=True)
        st.download_button("⬇️ " + t["news_download"], doc, file_name="newsletter.html", mime="text/html")
