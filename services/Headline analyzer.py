import re
import streamlit as st
from translations import translations

# English-oriented "power words" — detection is best for EN headlines.
POWER_WORDS = {
    "free", "new", "now", "best", "easy", "proven", "instantly", "guaranteed", "save", "boost",
    "ultimate", "exclusive", "secret", "powerful", "essential", "fast", "top", "smart", "win",
    "discover", "unlock", "results", "today", "how", "why", "you", "your",
}


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["head_title"])

    headline = st.text_input(t["head_input"])
    if not headline.strip():
        st.info(t["head_empty"])
        return

    chars = len(headline)
    words = re.findall(r"[^\W_]+", headline, flags=re.UNICODE)
    n_words = len(words)
    powers = [w for w in words if w.lower() in POWER_WORDS]
    has_number = bool(re.search(r"\d", headline))

    score = 40
    if 40 <= chars <= 60:
        score += 25
    elif 30 <= chars <= 70:
        score += 12
    if 6 <= n_words <= 12:
        score += 15
    if powers:
        score += 12
    if has_number:
        score += 8
    score = min(100, score)

    c1, c2, c3 = st.columns(3)
    c1.metric(t["head_chars"], chars)
    c2.metric(t["head_words"], n_words)
    c3.metric(t["head_score"], f"{score}/100")

    st.write(f"**{t['head_power']}:** " + (", ".join(powers) if powers else "—"))
    st.caption(t["head_tip_len"])
