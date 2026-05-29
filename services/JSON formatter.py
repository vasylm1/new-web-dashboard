import io
import json
import pandas as pd
import streamlit as st
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["json_title"])

    raw = st.text_area(t["json_input"], height=240, placeholder='{"hello": "world"}')
    indent = st.slider(t["json_indent"], 0, 8, 2)

    c1, c2, c3 = st.columns(3)
    do_format = c1.button("✨ " + t["json_format"], use_container_width=True)
    do_min = c2.button("🗜️ " + t["json_minify"], use_container_width=True)
    do_csv = c3.button("📑 " + t["json_to_csv"], use_container_width=True)

    if not (do_format or do_min or do_csv):
        return
    if not raw.strip():
        st.warning(t["json_empty"])
        return
    try:
        obj = json.loads(raw)
    except Exception as e:
        st.error(f"{t['json_invalid']} {e}")
        return

    st.success(t["json_valid"])

    if do_csv:
        try:
            df = pd.json_normalize(obj)
            st.dataframe(df.head(50), use_container_width=True)
            buf = io.BytesIO()
            df.to_csv(buf, index=False)
            st.download_button("⬇️ " + t["json_download_csv"], buf.getvalue(), file_name="data.csv", mime="text/csv")
        except Exception as e:
            st.error(str(e))
        return

    if do_min:
        out = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    else:
        out = json.dumps(obj, ensure_ascii=False, indent=indent)
    st.code(out, language="json")
    st.download_button("⬇️ " + t["json_download"], out, file_name="formatted.json", mime="application/json")
