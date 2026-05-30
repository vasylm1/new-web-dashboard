import sqlparse
import streamlit as st
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["sql_title"])

    raw = st.text_area(t["sql_input"], height=240, placeholder="select id,name from users where age>18 order by name")
    upper = st.checkbox(t["sql_keywords_upper"], value=True)

    if not st.button("✨ " + t["sql_format"]):
        return
    if not raw.strip():
        st.warning(t["sql_empty"])
        return

    formatted = sqlparse.format(
        raw,
        reindent=True,
        keyword_case="upper" if upper else None,
        identifier_case=None,
        use_space_around_operators=True,
    )
    st.code(formatted, language="sql")
    st.download_button("⬇️ " + t["sql_download"], formatted, file_name="formatted.sql", mime="text/plain")
