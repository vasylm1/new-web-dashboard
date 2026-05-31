import streamlit as st

# Keep in sync with PRIVACY.md.
LAST_UPDATED = "2026-05-31"
OPERATOR = "Vasyl Madei"
CONTACT_EMAIL = "vasylmadei@gmail.com"

# English fallbacks so the page renders even on a partial/stale translations load
# (mirrors the resilience built into main.py's _UI_DEFAULTS).
_DEFAULTS = {
    "privacy_title": "Privacy",
    "privacy_updated": "Last updated",
    "privacy_text": (
        "Files you upload are processed in memory to perform the conversion and are "
        "not stored on a server or shared with third parties. The YouTube-to-Markdown "
        "tool sends the URL to YouTube to fetch the transcript."
    ),
    "privacy_point_storage": (
        "**In-memory only.** Files you upload are processed in memory to produce your "
        "result and are never written to a database or persistent storage."
    ),
    "privacy_point_tracking": (
        "**No tracking.** No analytics or advertising cookies are used, and Streamlit's "
        "anonymous usage statistics are disabled."
    ),
    "privacy_point_thirdparty": (
        "**Third parties.** Only when you use a specific feature: a YouTube URL is sent "
        "to YouTube for its transcript, and PDF→MP3 text is sent to Google Text-to-Speech."
    ),
    "privacy_controller_title": "Data controller",
    "privacy_legal_title": "Legal basis",
    "privacy_legal_text": (
        "Processing is based on our legitimate interest (Art. 6(1)(f) GDPR) in providing "
        "the tool you request. Entering personal data is never required; if you do, you "
        "provide it voluntarily."
    ),
    "privacy_thirdparties_title": "Third-party services",
    "privacy_thirdparties_text": (
        "Only when you use a specific tool is data sent out: Google Text-to-Speech "
        "(PDF → MP3), YouTube (YouTube → Markdown) and open.er-api.com (currency rates). "
        "These providers may process data outside the EU/EEA (e.g. the USA)."
    ),
    "privacy_rights_title": "Your rights",
    "privacy_rights_text": (
        "You have the right to access, rectification, erasure, restriction, objection and "
        "data portability, and to lodge a complaint with a supervisory authority. As the "
        "app keeps nothing after your session, there is normally no stored data to act on."
    ),
    "privacy_contact_title": "Contact",
}


def render(t):
    """Privacy / GDPR policy page."""
    t = {**_DEFAULTS, **t}
    st.title(f"🔒 {t['privacy_title']}")
    st.caption(f"{t['privacy_updated']}: {LAST_UPDATED}")

    st.write(t["privacy_text"])
    st.markdown(f"💾 {t['privacy_point_storage']}")
    st.markdown(f"🚫 {t['privacy_point_tracking']}")
    st.markdown(f"🌐 {t['privacy_point_thirdparty']}")
    st.divider()

    st.subheader(t["privacy_controller_title"])
    st.markdown(f"{OPERATOR} · [{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")

    st.subheader(t["privacy_legal_title"])
    st.write(t["privacy_legal_text"])

    st.subheader(t["privacy_thirdparties_title"])
    st.write(t["privacy_thirdparties_text"])

    st.subheader(t["privacy_rights_title"])
    st.write(t["privacy_rights_text"])

    st.subheader(t["privacy_contact_title"])
    st.markdown(f"[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")
