# services/xls_to_ical.py
import uuid
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone
from translations import translations


def format_date(dt):
    if pd.isna(dt):
        return ""
    if isinstance(dt, float):
        dt = pd.to_datetime("1899-12-30") + pd.to_timedelta(dt, unit="D")
    elif isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except Exception:
            return ""
    elif not isinstance(dt, pd.Timestamp):
        try:
            dt = pd.to_datetime(dt)
        except Exception:
            return ""
    return dt.strftime("%Y%m%dT%H%M%S")


def escape_ics(value):
    """Escape text per RFC 5545 (backslash, comma, semicolon, newline)."""
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace(",", "\\,")
    text = text.replace(";", "\\;")
    text = text.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return text


def generate_ics(df):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//My Tools Hub//EN",
        "CALSCALE:GREGORIAN",
    ]
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for _, row in df.iterrows():
        start = format_date(row[0])
        end = format_date(row[1])
        if not start or not end:
            continue  # skip rows without a valid time range
        title = row[2] if pd.notna(row[2]) else "Event"
        description = row[3] if pd.notna(row[3]) else ""
        location = row[4] if pd.notna(row[4]) else ""
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uuid.uuid4()}@my-tools-hub")
        lines.append(f"DTSTAMP:{dtstamp}")
        lines.append(f"DTSTART:{start}")
        lines.append(f"DTEND:{end}")
        lines.append(f"SUMMARY:{escape_ics(title)}")
        if description:
            lines.append(f"DESCRIPTION:{escape_ics(description)}")
        if location:
            lines.append(f"LOCATION:{escape_ics(location)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    # RFC 5545 mandates CRLF line endings.
    return "\r\n".join(lines)


def get_template_file():
    sample = pd.DataFrame([
        ["2023-01-01 09:00", "2023-01-01 10:00", "Team Meeting", "Weekly sync", "Conference Room A"],
        ["2023-01-02 14:00", "2023-01-02 15:30", "Client Call", "Project discussion", "Zoom"],
        ["2023-01-03 10:00", "2023-01-03 12:00", "Workshop", "Training session", "Training Room"],
    ], columns=["Start Date", "End Date", "Event Title", "Description", "Location"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        sample.to_excel(writer, index=False, sheet_name="Events")
    return output.getvalue()


def run(lang):
    t = translations.get(lang, translations["English"])

    st.markdown(f"### {t['ical_title']}")

    st.markdown(f"#### 📘 {t['ical_instructions']}")
    st.download_button(f"📥 {t['ical_template']}", get_template_file(), file_name="Calendar_Template.xlsx")

    uploaded_file = st.file_uploader(t["ical_upload"], type=["xls", "xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.markdown(f"### 📊 {t['ical_preview']}")
            st.dataframe(df)

            if st.button(f"🔁 {t['ical_convert']}"):
                ics_content = generate_ics(df)
                st.download_button(f"📤 {t['ical_download']}", data=ics_content, file_name="calendar.ics", mime="text/calendar")
        except Exception as e:
            st.error(t["ical_error"] + str(e))
