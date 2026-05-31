import json
import urllib.request
import streamlit as st
from translations import translations

CURRENCIES = ["USD", "EUR", "PLN", "GBP", "UAH", "CHF", "JPY", "CNY", "CAD",
              "AUD", "SEK", "NOK", "CZK", "HUF", "TRY", "DKK"]

SYMBOLS = {
    "USD": "$", "EUR": "€", "PLN": "zł", "GBP": "£", "UAH": "₴", "CHF": "CHF",
    "JPY": "¥", "CNY": "¥", "CAD": "C$", "AUD": "A$", "SEK": "kr", "NOK": "kr",
    "CZK": "Kč", "HUF": "Ft", "TRY": "₺", "DKK": "kr",
}


@st.cache_data(ttl=3600, show_spinner=False)
def _rates(base):
    """Fetch live rates (keyless API). Cached for an hour."""
    url = f"https://open.er-api.com/v6/latest/{base}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("result") != "success":
        raise RuntimeError("rates unavailable")
    return data["rates"]


def _fmt(value):
    return f"{value:,.4f}" if value < 1 else f"{value:,.2f}"


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["cur_title"])
    st.caption(t["net_warning"])  # currency codes are sent to open.er-api.com

    mode_map = {t["cur_mode_one"]: "one", t["cur_mode_all"]: "all"}
    mode = mode_map[st.radio(t["batch_mode"], list(mode_map.keys()), horizontal=True)]

    left, right = st.columns([1, 1], gap="large")

    if mode == "one":
        with left:
            amount = st.number_input(t["cur_amount"], value=100.0, min_value=0.0)
            frm = st.selectbox(t["cur_from"], CURRENCIES, index=1)
            to = st.selectbox(t["cur_to"], CURRENCIES, index=2)
        try:
            rate = _rates(frm).get(to)
        except Exception:
            st.error(t["cur_error"])
            return
        if rate is None:
            st.error(t["cur_error"])
            return
        with right:
            st.metric(t["cur_result"], f"{amount * rate:,.2f} {to}")
            st.caption(f"{t['cur_rate']}: 1 {frm} = {rate:.4f} {to}")
        st.caption(t["cur_note"])
        return

    # One-to-many: base amount converted into every other currency.
    with left:
        amount = st.number_input(t["cur_amount"], value=1.0, min_value=0.0)
        base = st.selectbox(t["cur_from"], CURRENCIES, index=2)
    try:
        rates = _rates(base)
    except Exception:
        st.error(t["cur_error"])
        return

    rows = ""
    for code in CURRENCIES:
        if code == base or code not in rates:
            continue
        value = amount * rates[code]
        rows += (
            '<div style="display:flex;justify-content:space-between;align-items:center;'
            'padding:9px 14px;border-bottom:1px solid #eef1f6;">'
            f'<span style="font-weight:600;color:#0f172a;">{code}</span>'
            f'<span style="color:#334155;">{_fmt(value)} {SYMBOLS.get(code, "")}</span></div>'
        )
    with right:
        st.caption(f"{amount:,.2f} {base} =")
        st.markdown(
            f'<div style="background:#fff;border:1px solid #e9edf4;border-radius:14px;overflow:hidden;">{rows}</div>',
            unsafe_allow_html=True,
        )
    st.caption(t["cur_note"])
