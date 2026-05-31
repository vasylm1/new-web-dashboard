import streamlit as st

# Operator / data controller (shown publicly as the legal contact).
OPERATOR = "Vasyl Madei"
CONTACT_EMAIL = "vasylmadei@gmail.com"

# English fallbacks so the page renders even on a partial/stale translations load
# (mirrors the resilience built into main.py's _UI_DEFAULTS).
_DEFAULTS = {
    "imprint_title": "Imprint / Legal Notice",
    "imprint_intro": "Information pursuant to applicable law (incl. § 5 DDG, Germany).",
    "imprint_responsible_label": "Responsible for content",
    "imprint_contact_label": "Contact",
    "imprint_disclaimer_title": "Disclaimer",
    "imprint_disclaimer_text": (
        "This app is provided “as is”, without warranty. Despite careful review we "
        "accept no liability for the content of external links — their operators are "
        "solely responsible. Results produced by the tools are provided without guarantee."
    ),
}


def render(t):
    t = {**_DEFAULTS, **t}
    st.title("⚖️ " + t["imprint_title"])
    st.caption(t["imprint_intro"])

    st.subheader(t["imprint_responsible_label"])
    st.write(OPERATOR)

    st.subheader(t["imprint_contact_label"])
    st.markdown(f"[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")

    st.divider()
    st.subheader(t["imprint_disclaimer_title"])
    st.write(t["imprint_disclaimer_text"])
