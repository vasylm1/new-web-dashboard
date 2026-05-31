import streamlit as st

# Keep in sync with PRIVACY.md.
LAST_UPDATED = "2026-05-31"
OPERATOR = "Vasyl Madei"
CONTACT_EMAIL = "vasylmadei@gmail.com"


def render(t):
    """Privacy / GDPR policy page."""
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
