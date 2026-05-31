import re
from collections import Counter
import streamlit as st
from translations import translations

STOPWORDS = set("""
a an the and or but of to in on for with at by from is are was were be this that it as not your you
i we they he she my our their de la le les et un une der die das und mit i w z na do nie to ta i j v
""".split())


def _syllables(word):
    word = word.lower()
    groups = re.findall(r"[aeiouyąęóуеёиыэюяäöü]+", word)
    return max(1, len(groups))


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["copyan_title"])

    text = st.text_area(t["copyan_input"], height=220)
    if not text.strip():
        st.info(t["copyan_empty"])
        return

    words = re.findall(r"[^\W\d_]+", text, flags=re.UNICODE)
    n_words = len(words)
    n_chars = len(text)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    n_sent = max(1, len(sentences))
    syllables = sum(_syllables(w) for w in words) or 1
    reading_min = max(1, round(n_words / 200))

    # Flesch Reading Ease (English-tuned; approximate for other languages).
    flesch = 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (syllables / max(1, n_words))
    flesch = max(0, min(100, round(flesch)))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t["copyan_words"], n_words)
    c2.metric(t["copyan_chars"], n_chars)
    c3.metric(t["copyan_sentences"], len(sentences))
    c4.metric(t["copyan_reading_time"], f"~{reading_min}")
    st.metric(t["copyan_readability"], flesch)

    common = [w for w in (w.lower() for w in words) if w not in STOPWORDS and len(w) > 2]
    top = Counter(common).most_common(10)
    if top:
        st.subheader(t["copyan_top_words"])
        st.write("  ·  ".join(f"**{w}** ({c})" for w, c in top))
