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


TABLE = 'cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;"'


def _photo_tag(uri, size, radius="50%"):
    if not uri:
        return ""
    return (f'<img src="{uri}" width="{size}" height="{size}" '
            f'style="border-radius:{radius};display:block;object-fit:cover;" alt="">')


def _parts(data):
    """Pre-build the shared, escaped HTML fragments every template reuses."""
    e = lambda v: html.escape(str(v), quote=True)
    base = data["font_size"]
    primary = data["primary_color"]

    contact_bits = []
    if data["phone"]:
        contact_bits.append(f'📞 {e(data["phone"])}')
    if data["email"]:
        contact_bits.append(
            f'✉️ <a href="mailto:{e(data["email"])}" style="color:{primary};text-decoration:none;">{e(data["email"])}</a>'
        )

    style = data["link_style"]
    links = []
    for label, emoji, url in data["socials"]:
        if not url:
            continue
        inner = emoji if style == "icon" else (e(label) if style == "text" else f"{emoji} {e(label)}")
        links.append(
            f'<a href="{e(url)}" style="color:{primary};text-decoration:none;font-weight:600;">{inner}</a>'
        )

    role_company = " · ".join(filter(None, [
        e(data["job_title"]) if data["job_title"] else "",
        e(data["company"]) if data["company"] else "",
    ]))
    greeting = e(data["greeting"]) if data["greeting"] else ""
    greeting_html = (f'<div style="font-size:{base}px;color:#6b7280;padding-bottom:10px;">{greeting}</div>'
                     if greeting else "")

    return {
        "font": data["font_family"], "base": base,
        "heading": round(base * data["heading_scale"] / 100),
        "primary": primary, "text": data["text_color"], "bg": data["bg_color"], "muted": "#6b7280",
        "name": e(data["full_name"]) or "&nbsp;",
        "role_company": role_company,
        "contact_inline": "&nbsp;&nbsp;|&nbsp;&nbsp;".join(contact_bits),
        "contact_stacked": "<br>".join(contact_bits),
        "social_line": "&nbsp;&nbsp;·&nbsp;&nbsp;".join(links),
        "greeting_html": greeting_html,
        "photo_uri": data["photo_uri"],
    }


def _wrap(p, inner, align="left"):
    return (f'<div style="font-family:{p["font"]};background:{p["bg"]};padding:16px;'
            f'display:inline-block;text-align:{align};">{p["greeting_html"]}{inner}</div>')


def _t1(p):  # Accent bar
    cell = f'<td style="padding-right:16px;vertical-align:top;">{_photo_tag(p["photo_uri"], 84)}</td>' if p["photo_uri"] else ""
    return _wrap(p, f'<table {TABLE}><tr>{cell}'
        f'<td style="vertical-align:top;border-left:3px solid {p["primary"]};padding-left:16px;">'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};padding-top:2px;">{p["role_company"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:8px;">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div>'
        f'</td></tr></table>')


def _t2(p):  # Top banner
    cell = f'<td style="padding-right:12px;vertical-align:middle;">{_photo_tag(p["photo_uri"], 56)}</td>' if p["photo_uri"] else ""
    header = (f'<table {TABLE}><tr>{cell}<td style="vertical-align:middle;">'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:#ffffff;">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:rgba(255,255,255,0.85);">{p["role_company"]}</div>'
        f'</td></tr></table>')
    return _wrap(p, f'<div style="background:{p["primary"]};padding:14px 16px;border-radius:8px 8px 0 0;">{header}</div>'
        f'<div style="padding:12px 16px;border:1px solid #e5e7eb;border-top:none;border-radius:0 0 8px 8px;">'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div></div>')


def _t3(p):  # Minimal
    return _wrap(p, f'<div style="border-top:2px solid {p["primary"]};padding-top:10px;">'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};padding-top:2px;">{p["role_company"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:6px;">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:6px;">{p["social_line"]}</div></div>')


def _t4(p):  # Card
    cell = f'<td style="padding-right:14px;vertical-align:top;">{_photo_tag(p["photo_uri"], 72)}</td>' if p["photo_uri"] else ""
    return _wrap(p, f'<div style="border:1px solid {p["primary"]};background:#f8fafc;border-radius:10px;padding:14px 16px;">'
        f'<table {TABLE}><tr>{cell}<td style="vertical-align:top;">'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};padding-top:2px;">{p["role_company"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:8px;">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div>'
        f'</td></tr></table></div>')


def _t5(p):  # Centered
    photo = f'<div style="padding-bottom:10px;">{_photo_tag(p["photo_uri"], 96)}</div>' if p["photo_uri"] else ""
    return _wrap(p, f'{photo}'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};padding-top:2px;">{p["role_company"]}</div>'
        f'<div style="width:40px;height:3px;background:{p["primary"]};margin:10px auto;"></div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div>', align="center")


def _t6(p):  # Two columns + divider
    photo = f'<div style="padding-bottom:8px;">{_photo_tag(p["photo_uri"], 72)}</div>' if p["photo_uri"] else ""
    left = (f'<td style="vertical-align:top;padding-right:18px;">{photo}'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};padding-top:2px;">{p["role_company"]}</div></td>')
    right = (f'<td style="vertical-align:top;border-left:2px solid {p["primary"]};padding-left:18px;">'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};line-height:1.6;">{p["contact_stacked"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div></td>')
    return _wrap(p, f'<table {TABLE}><tr>{left}{right}</tr></table>')


def _t7(p):  # Bold name + underline
    return _wrap(p, f'<div style="font-size:{p["heading"] + 4}px;font-weight:800;color:{p["primary"]};">{p["name"]}</div>'
        f'<div style="border-bottom:2px solid {p["primary"]};width:120px;margin:4px 0 8px;"></div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};">{p["role_company"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:8px;">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div>')


def _t8(p):  # Compact
    cell = f'<td style="padding-right:12px;vertical-align:top;">{_photo_tag(p["photo_uri"], 56)}</td>' if p["photo_uri"] else ""
    return _wrap(p, f'<table {TABLE}><tr>{cell}<td style="vertical-align:top;">'
        f'<div style="font-size:{p["base"] + 2}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};">{p["role_company"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:4px;line-height:1.5;">{p["contact_stacked"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:4px;">{p["social_line"]}</div>'
        f'</td></tr></table>')


def _t9(p):  # Role pill
    pill = (f'<span style="display:inline-block;background:{p["primary"]};color:#fff;'
        f'font-size:{p["base"]}px;padding:2px 10px;border-radius:12px;">{p["role_company"]}</span>'
        if p["role_company"] else "")
    cell = f'<td style="padding-right:16px;vertical-align:top;">{_photo_tag(p["photo_uri"], 80)}</td>' if p["photo_uri"] else ""
    return _wrap(p, f'<table {TABLE}><tr>{cell}<td style="vertical-align:top;">'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};padding-bottom:6px;">{p["name"]}</div>'
        f'<div>{pill}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:8px;">{p["contact_inline"]}</div>'
        f'<div style="font-size:{p["base"]}px;padding-top:8px;">{p["social_line"]}</div>'
        f'</td></tr></table>')


def _t10(p):  # Modern rules
    cell = f'<td style="padding-right:14px;vertical-align:middle;">{_photo_tag(p["photo_uri"], 64)}</td>' if p["photo_uri"] else ""
    top = (f'<table {TABLE}><tr>{cell}<td style="vertical-align:middle;">'
        f'<div style="font-size:{p["heading"]}px;font-weight:700;color:{p["text"]};">{p["name"]}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["muted"]};">{p["role_company"]}</div></td></tr></table>')
    return _wrap(p, f'<div style="border-top:2px solid {p["primary"]};border-bottom:2px solid {p["primary"]};padding:12px 0;">{top}</div>'
        f'<div style="font-size:{p["base"]}px;color:{p["text"]};padding-top:8px;">{p["contact_inline"]}'
        f'&nbsp;&nbsp;|&nbsp;&nbsp;{p["social_line"]}</div>')


TEMPLATES = [_t1, _t2, _t3, _t4, _t5, _t6, _t7, _t8, _t9, _t10]


def build_signature(data, design=1):
    """Render the chosen design (1-10) as an inline-styled HTML signature."""
    p = _parts(data)
    idx = max(1, min(len(TEMPLATES), int(design))) - 1
    return TEMPLATES[idx](p)


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["email_signature_title"])

    # Pick one random demo persona per session (stable across reruns).
    if "sig_sample" not in st.session_state:
        st.session_state.sig_sample = random.choice(SAMPLE_PERSONAS)
    sample = st.session_state.sig_sample

    left, right = st.columns([1, 1], gap="large")

    with left:
        design = st.selectbox(
            "🎨 " + t["sig_design"],
            list(range(1, len(TEMPLATES) + 1)),
            format_func=lambda n: f"{t['sig_design']} {n}",
        )
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

    signature_html = build_signature(data, design)

    with right:
        st.subheader(t["preview"])
        components.html(signature_html, height=320, scrolling=True)

        st.download_button(
            "⬇️ " + t["download_html"],
            data=signature_html,
            file_name="email_signature.html",
            mime="text/html",
            use_container_width=True,
        )
        st.caption(t["copy_clipboard"])
        st.code(signature_html, language="html")
