import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from translations import translations


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["chart_title"])

    up = st.file_uploader(t["chart_upload"], type=["csv", "xlsx", "xls"])
    if not up:
        return
    try:
        df = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
    except Exception as e:
        st.error(f"{t['chart_error']} {e}")
        return

    st.dataframe(df.head(20), use_container_width=True)
    cols = list(df.columns)
    type_map = {t["chart_bar"]: "bar", t["chart_line"]: "line", t["chart_pie"]: "pie"}
    ctype = type_map[st.selectbox(t["chart_type"], list(type_map.keys()))]
    x = st.selectbox(t["chart_x"], cols)
    y = st.selectbox(t["chart_y"], [c for c in cols if c != x] or cols)

    if not st.button("📈 " + t["chart_make"]):
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    try:
        data = df[[x, y]].dropna()
        if ctype == "bar":
            ax.bar(data[x].astype(str), pd.to_numeric(data[y], errors="coerce"))
            ax.tick_params(axis="x", rotation=45)
        elif ctype == "line":
            ax.plot(data[x].astype(str), pd.to_numeric(data[y], errors="coerce"), marker="o")
            ax.tick_params(axis="x", rotation=45)
        else:  # pie
            ax.pie(pd.to_numeric(data[y], errors="coerce").fillna(0), labels=data[x].astype(str), autopct="%1.0f%%")
        ax.set_title(f"{y} / {x}")
        fig.tight_layout()
    except Exception as e:
        st.error(f"{t['chart_error']} {e}")
        return

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    st.image(buf.getvalue(), use_container_width=True)
    st.download_button("⬇️ " + t["chart_download"], buf.getvalue(), file_name="chart.png", mime="image/png")
