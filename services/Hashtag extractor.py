import re
from collections import Counter
import streamlit as st
from translations import translations

# Small multilingual stopword set (EN/FR/DE/PL/UK) — good enough for keyword ranking.
STOPWORDS = set("""
a an the and or but if then else of to in on for with at by from up about into over after before
is are was were be been being do does did this that these those it its as not no nor so than too very
he she they we you i your our their his her them him me my mine ours yours has have had will would can
de la le les des et un une du au aux pour avec sur dans par ne pas plus
der die das und oder aber mit fur von zu im am ist sind ein eine den dem auch nicht
i w z na do nie to sie ze jest sa oraz dla od po jak co czy tak ten ta te
ta i j v na z do ne shcho tse yak dlya bo ale abo ki vsi tilky
""".split())


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["kw_title"])

    text = st.text_area(t["kw_input"], height=200)
    n = st.slider(t["kw_count"], 5, 30, 12)

    if not st.button(t["kw_extract"]):
        return
    if not text.strip():
        st.warning(t["kw_empty"])
        return

    found = list(dict.fromkeys(re.findall(r"#(\w+)", text)))  # preserve order, unique
    words = re.findall(r"[^\W\d_]{3,}", text.lower(), flags=re.UNICODE)
    words = [w for w in words if w not in STOPWORDS]
    top = Counter(words).most_common(n)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t["kw_keywords"])
        for w, c in top:
            st.write(f"**{w}** · {c}")
    with col2:
        st.subheader(t["kw_hashtags"])
        st.code(" ".join("#" + w for w, _ in top), language=None)

    if found:
        st.subheader(t["kw_found_hashtags"])
        st.write(" ".join("#" + h for h in found))
