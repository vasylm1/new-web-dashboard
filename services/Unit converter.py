import streamlit as st
from translations import translations

# Factor to the base unit of each category.
UNITS = {
    "length": {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048, "mi": 1609.344},
    "mass": {"mg": 1e-6, "g": 0.001, "kg": 1.0, "t": 1000.0, "oz": 0.0283495, "lb": 0.453592},
    "data": {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4},
}


def _convert_temp(value, frm, to):
    c = value if frm == "°C" else (value - 32) * 5 / 9 if frm == "°F" else value - 273.15
    return c if to == "°C" else c * 9 / 5 + 32 if to == "°F" else c + 273.15


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["unit_title"])

    cat_map = {t["unit_length"]: "length", t["unit_mass"]: "mass", t["unit_temp"]: "temp", t["unit_data"]: "data"}
    cat = cat_map[st.selectbox(t["unit_category"], list(cat_map.keys()))]

    value = st.number_input(t["unit_value"], value=1.0)
    units = ["°C", "°F", "K"] if cat == "temp" else list(UNITS[cat].keys())
    c1, c2 = st.columns(2)
    frm = c1.selectbox(t["unit_from"], units, index=0)
    to = c2.selectbox(t["unit_to"], units, index=min(1, len(units) - 1))

    if cat == "temp":
        result = _convert_temp(value, frm, to)
    else:
        result = value * UNITS[cat][frm] / UNITS[cat][to]

    st.metric(t["unit_result"], f"{result:.6g} {to}")
