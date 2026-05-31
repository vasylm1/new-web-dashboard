import io
import pandas as pd
import streamlit as st
from faker import Faker
from translations import translations

# App language -> Faker locale for region-appropriate sample data.
LOCALES = {"English": "en_US", "Polski": "pl_PL", "Deutsch": "de_DE", "Українська": "uk_UA", "中文": "zh_CN"}


def run(lang):
    t = translations.get(lang, translations["English"])
    st.title(t["faker_title"])

    fields = {
        t["faker_f_name"]: lambda f: f.name(),
        t["faker_f_email"]: lambda f: f.email(),
        t["faker_f_phone"]: lambda f: f.phone_number(),
        t["faker_f_company"]: lambda f: f.company(),
        t["faker_f_address"]: lambda f: f.address().replace("\n", ", "),
        t["faker_f_city"]: lambda f: f.city(),
        t["faker_f_country"]: lambda f: f.country(),
        t["faker_f_job"]: lambda f: f.job(),
        t["faker_f_date"]: lambda f: f.date(),
    }

    rows = st.slider(t["faker_rows"], 5, 500, 50)
    chosen = st.multiselect(t["faker_fields"], list(fields.keys()),
                            default=[t["faker_f_name"], t["faker_f_email"], t["faker_f_company"]])

    if not st.button("🎲 " + t["faker_generate"]) or not chosen:
        return

    fake = Faker(LOCALES.get(lang, "en_US"))
    data = {col: [fields[col](fake) for _ in range(rows)] for col in chosen}
    df = pd.DataFrame(data)
    st.dataframe(df.head(50), use_container_width=True)

    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    st.download_button("⬇️ " + t["faker_download"], buf.getvalue(), file_name="sample_data.csv", mime="text/csv")
