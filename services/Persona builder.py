import html
import streamlit as st
import streamlit.components.v1 as components
from translations import translations


def _card(title, body, primary):
    body = html.escape(body).replace("\n", "<br>")
    return (f'<div style="border:1px solid #e5e7eb;border-radius:10px;padding:12px 14px;margin-bottom:10px;">'
            f'<div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:{primary};'
            f'font-weight:700;margin-bottom:4px;">{html.escape(title)}</div>'
            f'<div style="font-size:14px;color:#1f2937;">{body or "—"}</div></div>')


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["persona_title"])

    left, right = st.columns([1, 1], gap="large")
    with left:
        name = st.text_input(t["persona_name"], placeholder="Marketing Mary")
        role = st.text_input(t["persona_role"], placeholder="Head of Marketing")
        industry = st.text_input(t["persona_industry"], placeholder="B2B SaaS")
        goals = st.text_area(t["persona_goals"], height=80)
        pains = st.text_area(t["persona_pains"], height=80)
        channels = st.text_input(t["persona_channels"], placeholder="LinkedIn, Email, Webinars")
        quote = st.text_input(t["persona_quote"])
        primary = st.color_picker(t["primary_color"], "#4361ee")

    if not name.strip():
        st.info(t["persona_empty"])
        return

    header = (f'<div style="background:{primary};color:#fff;border-radius:10px;padding:16px;margin-bottom:12px;">'
              f'<div style="font-size:20px;font-weight:800;">{html.escape(name)}</div>'
              f'<div style="opacity:.9;">{html.escape(" · ".join(filter(None, [role, industry])))}</div></div>')
    quote_html = (f'<div style="font-style:italic;color:#374151;border-left:3px solid {primary};'
                  f'padding-left:12px;margin-bottom:12px;">“{html.escape(quote)}”</div>' if quote.strip() else "")
    cards = (_card(t["persona_goals"], goals, primary) + _card(t["persona_pains"], pains, primary)
             + _card(t["persona_channels"], channels, primary))
    page = (f'<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;">{header}{quote_html}{cards}</div>')

    with right:
        st.subheader(t["preview"])
        components.html(page, height=520, scrolling=True)
        full = f"<!doctype html><html><head><meta charset='utf-8'></head><body>{page}</body></html>"
        st.download_button("⬇️ " + t["persona_download"], full, file_name="persona.html", mime="text/html")
