import difflib
import html
import streamlit as st
import streamlit.components.v1 as components
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["diff_title"])

    c1, c2 = st.columns(2)
    left = c1.text_area(t["diff_left"], height=240)
    right = c2.text_area(t["diff_right"], height=240)

    if not left.strip() and not right.strip():
        return

    a, b = left.splitlines(), right.splitlines()
    if a == b:
        st.success(t["diff_identical"])
        return

    added = removed = 0
    rows = []
    for line in difflib.ndiff(a, b):
        tag, content = line[:2], html.escape(line[2:])
        if tag == "+ ":
            added += 1
            rows.append(f'<div style="background:#dcfce7;color:#166534;padding:1px 6px;">+ {content}</div>')
        elif tag == "- ":
            removed += 1
            rows.append(f'<div style="background:#fee2e2;color:#991b1b;padding:1px 6px;">- {content}</div>')
        elif tag == "  ":
            rows.append(f'<div style="color:#6b7280;padding:1px 6px;">&nbsp;&nbsp;{content}</div>')

    st.write(f"**{t['diff_added']}:** {added} · **{t['diff_removed']}:** {removed}")
    body = "<div style='font-family:monospace;font-size:13px;line-height:1.5;'>" + "".join(rows) + "</div>"
    components.html(body, height=360, scrolling=True)
