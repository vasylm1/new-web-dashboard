import base64
import html
import random
import streamlit as st
import streamlit.components.v1 as components
from translations import translations

# Neutral demo identities used only to populate the preview before the user
# types anything. Order matches SOCIALS (LinkedIn, X, GitHub, Instagram, Website).
SAMPLE_PERSONAS = [
    {
        "full_name": "Jane Doe", "job_title": "Marketing Manager", "company": "Acme Inc.",
        "phone": "+1 555 0100", "email": "jane.doe@example.com",
        "socials": ["https://www.linkedin.com/in/janedoe", "https://x.com/janedoe", "", "", "https://example.com"],
    },
    {
        "full_name": "Alex Rivera", "job_title": "Product Designer", "company": "Globex",
        "phone": "+44 20 7946 0000", "email": "alex.rivera@example.com",
        "socials": ["https://www.linkedin.com/in/alexrivera", "", "https://github.com/alexrivera", "", "https://example.org"],
    },
    {
        "full_name": "Sam Kowalski", "job_title": "Sales Lead", "company": "Initech",
        "phone": "+49 30 901820", "email": "sam.kowalski@example.com",
        "socials": ["https://www.linkedin.com/in/samkowalski", "https://x.com/samk", "", "https://instagram.com/samk", ""],
    },
]

# (label, emoji, placeholder) for the social links in the "Connect" section.
SOCIALS = [
    ("LinkedIn", "🔗", "https://www.linkedin.com/in/username"),
    ("X", "𝕏", "https://x.com/username"),
    ("GitHub", "💻", "https://github.com/username"),
    ("Instagram", "📸", "https://instagram.com/username"),
    ("Website", "🌐", "https://example.com"),
]

FONTS = [
    "Arial, sans-serif",
    "Helvetica, Arial, sans-serif",
    "Georgia, serif",
    "'Segoe UI', sans-serif",
    "'Times New Roman', serif",
    "Verdana, sans-serif",
]


def _photo_data_uri(uploaded_file):
    """Return a base64 data URI so the signature HTML is self-contained."""
    data = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/png"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_signature(data):
    """Build an email-client-friendly, table-based HTML signature with inline styles."""
    e = lambda v: html.escape(str(v), quote=True)
    font = data["font_family"]
    base = data["font_size"]
    heading = round(base * data["heading_scale"] / 100)
    primary = data["primary_color"]
    text_color = data["text_color"]
    bg = data["bg_color"]
    muted = "#6b7280"

    # Contact rows
    contact_bits = []
    if data["phone"]:
        contact_bits.append(f'📞 {e(data["phone"])}')
    if data["email"]:
        contact_bits.append(
            f'✉️ <a href="mailto:{e(data["email"])}" style="color:{primary};text-decoration:none;">{e(data["email"])}</a>'
        )
    contact_line = "&nbsp;&nbsp;|&nbsp;&nbsp;".join(contact_bits)

    # Social links
    style = data["link_style"]
    links = []
    for label, emoji, url in data["socials"]:
        if not url:
            continue
        if style == "icon":
            inner = emoji
        elif style == "text":
            inner = e(label)
        else:  # both
            inner = f"{emoji} {e(label)}"
        links.append(
            f'<a href="{e(url)}" style="color:{primary};text-decoration:none;font-weight:600;">{inner}</a>'
        )
    social_line = "&nbsp;&nbsp;·&nbsp;&nbsp;".join(links)

    photo_cell = ""
    if data["photo_uri"]:
        photo_cell = (
            f'<td style="padding-right:16px;vertical-align:top;">'
            f'<img src="{data["photo_uri"]}" width="84" height="84" '
            f'style="border-radius:50%;display:block;object-fit:cover;" alt=""></td>'
        )

    greeting_html = ""
    if data["greeting"]:
        greeting_html = (
            f'<div style="font-size:{base}px;color:{muted};padding-bottom:10px;">{e(data["greeting"])}</div>'
        )

    role_company = " · ".join(filter(None, [e(data["job_title"]) if data["job_title"] else "",
                                            e(data["company"]) if data["company"] else ""]))

    return f"""<div style="font-family:{font};background:{bg};padding:16px;display:inline-block;">
{greeting_html}<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
<tr>{photo_cell}<td style="vertical-align:top;border-left:3px solid {primary};padding-left:16px;">
<div style="font-size:{heading}px;font-weight:700;color:{text_color};">{e(data["full_name"]) or "&nbsp;"}</div>
<div style="font-size:{base}px;color:{muted};padding-top:2px;">{role_company}</div>
<div style="font-size:{base}px;color:{text_color};padding-top:8px;">{contact_line}</div>
<div style="font-size:{base}px;padding-top:8px;">{social_line}</div>
</td></tr></table></div>"""


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["email_signature_title"])

    # Pick one random demo persona per session (stable across reruns).
    if "sig_sample" not in st.session_state:
        st.session_state.sig_sample = random.choice(SAMPLE_PERSONAS)
    sample = st.session_state.sig_sample

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader(t["signature_details"])
        full_name = st.text_input(t["full_name"], placeholder=sample["full_name"])
        job_title = st.text_input(t["job_title"], placeholder=sample["job_title"])
        company = st.text_input(t["company_name"], placeholder=sample["company"])

        st.markdown(f"**{t['contact_info']}**")
        phone = st.text_input(t["phone_number"], placeholder=sample["phone"])
        email = st.text_input(t["email"], placeholder=sample["email"])
        greeting = st.text_input(t["greeting_label"], value=t["greeting_default"])

        st.markdown(f"**{t['connect_title']}**")
        st.caption(t["connect_subtitle"])
        socials = []
        for i, (label, emoji, placeholder) in enumerate(SOCIALS):
            ph = sample["socials"][i] or placeholder
            url = st.text_input(f"{emoji} {label}", placeholder=ph, key=f"sig_{label}")
            socials.append((label, emoji, url.strip()))

        st.markdown(f"**{t['profile_photo']}**")
        photo = st.file_uploader(t["upload_photo"], type=["png", "jpg", "jpeg", "webp"])

        with st.expander(t["appearance_title"]):
            c1, c2, c3 = st.columns(3)
            primary_color = c1.color_picker(t["primary_color"], "#4361ee")
            text_color = c2.color_picker(t["text_color"], "#1f2937")
            bg_color = c3.color_picker(t["bg_color"], "#ffffff")
            font_family = st.selectbox(t["font_family"], FONTS)
            font_size = st.slider(t["font_size"], 11, 18, 14)
            heading_scale = st.slider(t["heading_scale"], 110, 200, 150, step=10)
            link_style_map = {
                t["link_style_both"]: "both",
                t["link_style_text"]: "text",
                t["link_style_icon"]: "icon",
            }
            link_style_label = st.radio(t["link_style"], list(link_style_map.keys()), horizontal=True)
            link_style = link_style_map[link_style_label]

    # Until the user enters anything, show the random demo persona in the preview.
    entered_socials = [u for _, _, u in socials if u]
    form_touched = any([full_name, job_title, company, phone.strip(), email.strip(), photo]) or entered_socials
    if form_touched:
        preview_socials = socials
    else:
        full_name, job_title, company = sample["full_name"], sample["job_title"], sample["company"]
        phone, email = sample["phone"], sample["email"]
        preview_socials = [(label, emoji, sample["socials"][i]) for i, (label, emoji, _) in enumerate(SOCIALS)]

    data = {
        "full_name": full_name,
        "job_title": job_title,
        "company": company,
        "phone": phone.strip(),
        "email": email.strip(),
        "greeting": greeting.strip(),
        "socials": preview_socials,
        "photo_uri": _photo_data_uri(photo) if photo else None,
        "primary_color": primary_color,
        "text_color": text_color,
        "bg_color": bg_color,
        "font_family": font_family,
        "font_size": font_size,
        "heading_scale": heading_scale,
        "link_style": link_style,
    }

    signature_html = build_signature(data)

    with right:
        st.subheader(t["preview"])
        components.html(signature_html, height=240, scrolling=True)

        st.download_button(
            "⬇️ " + t["download_html"],
            data=signature_html,
            file_name="email_signature.html",
            mime="text/html",
            use_container_width=True,
        )
        st.caption(t["copy_clipboard"])
        st.code(signature_html, language="html")
