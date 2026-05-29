import streamlit as st

# Keep in sync with PRIVACY.md.
LAST_UPDATED = "2026-05-29"


def render(t):
    """Privacy / GDPR page."""
    st.title(f"🔒 {t['privacy_title']}")
    st.caption(f"{t['privacy_updated']}: {LAST_UPDATED}")

    st.write(t["privacy_text"])
    st.divider()

    st.markdown(f"💾 {t['privacy_point_storage']}")
    st.markdown(f"🚫 {t['privacy_point_tracking']}")
    st.markdown(f"🌐 {t['privacy_point_thirdparty']}")
