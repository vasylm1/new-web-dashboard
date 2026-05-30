import json
import urllib.request
import streamlit as st
from translations import translations

CURRENCIES = ["USD", "EUR", "PLN", "GBP", "UAH", "CHF", "JPY", "CNY", "CAD", "AUD", "SEK", "NOK", "CZK"]


@st.cache_data(ttl=3600, show_spinner=False)
def _rates(base):
    """Fetch live rates (keyless API). Cached for an hour."""
    url = f"https://open.er-api.com/v6/latest/{base}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("result") != "success":
        raise RuntimeError("rates unavailable")
    return data["rates"]


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["cur_title"])

    amount = st.number_input(t["cur_amount"], value=100.0, min_value=0.0)
    c1, c2 = st.columns(2)
    frm = c1.selectbox(t["cur_from"], CURRENCIES, index=1)
    to = c2.selectbox(t["cur_to"], CURRENCIES, index=2)

    if st.button("💱 " + t["cur_convert"]):
        try:
            rates = _rates(frm)
        except Exception:
            st.error(t["cur_error"])
            return
        rate = rates.get(to)
        if rate is None:
            st.error(t["cur_error"])
            return
        st.metric(t["cur_result"], f"{amount * rate:,.2f} {to}")
        st.caption(f"{t['cur_rate']}: 1 {frm} = {rate:.4f} {to}")

    st.caption(t["cur_note"])
