import streamlit as st

# Operator / data controller (shown publicly as the legal contact).
OPERATOR = "Vasyl Madei"
CONTACT_EMAIL = "vasylmadei@gmail.com"


def render(t):
    st.title("⚖️ " + t["imprint_title"])
    st.caption(t["imprint_intro"])

    st.subheader(t["imprint_responsible_label"])
    st.write(OPERATOR)

    st.subheader(t["imprint_contact_label"])
    st.markdown(f"[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")

    st.divider()
    st.subheader(t["imprint_disclaimer_title"])
    st.write(t["imprint_disclaimer_text"])
