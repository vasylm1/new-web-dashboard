from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from translations import translations

TIMEZONES = [
    "UTC", "Europe/Warsaw", "Europe/Berlin", "Europe/London", "Europe/Kyiv",
    "America/New_York", "America/Los_Angeles", "Asia/Dubai", "Asia/Shanghai", "Asia/Tokyo",
]


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["dt_title"])

    mode_map = {t["dt_diff"]: "diff", t["dt_workdays"]: "work", t["dt_tz"]: "tz"}
    mode = mode_map[st.radio(t["dt_mode"], list(mode_map.keys()), horizontal=True)]

    if mode in ("diff", "work"):
        c1, c2 = st.columns(2)
        start = c1.date_input(t["dt_start"], date.today())
        end = c2.date_input(t["dt_end"], date.today() + timedelta(days=7))
        if mode == "diff":
            days = (end - start).days
            st.metric(t["dt_result"], f"{days} {t['dt_days']}")
        else:
            n = int(len(pd.bdate_range(min(start, end), max(start, end))))
            st.metric(t["dt_result"], f"{n} {t['dt_days']}")
    else:  # timezone conversion
        c1, c2 = st.columns(2)
        d = c1.date_input(t["dt_datetime"], date.today())
        tm = c2.time_input(" ", time(12, 0))
        c3, c4 = st.columns(2)
        from_tz = c3.selectbox(t["dt_from_tz"], TIMEZONES, index=1)
        to_tz = c4.selectbox(t["dt_to_tz"], TIMEZONES, index=0)
        src = datetime.combine(d, tm, tzinfo=ZoneInfo(from_tz))
        dst = src.astimezone(ZoneInfo(to_tz))
        st.metric(t["dt_result"], dst.strftime("%Y-%m-%d %H:%M"))
        st.caption(f"{from_tz} → {to_tz}")
