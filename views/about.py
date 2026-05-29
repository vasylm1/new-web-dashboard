import streamlit as st

LINKEDIN_URL = "https://www.linkedin.com/in/vasyl-madei-399488247/"


def render(t):
    """About Me page."""
    st.title(f"👤 {t['aboutTitle']}")
    st.markdown(f"#### {t['aboutText1']}")
    st.divider()

    # Intro + remaining sections.
    st.markdown(t["aboutText2"])
    st.markdown(t["aboutText3"])
    st.markdown(t["aboutText4"])

    st.divider()
    st.subheader(t["about_connect"])
    st.markdown(
        f"""
        <a class="social-link" href="{LINKEDIN_URL}" target="_blank" rel="noopener">
          🔗 {t["linkedinText"]}
        </a>
        """,
        unsafe_allow_html=True,
    )
