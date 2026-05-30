import streamlit as st
from io import BytesIO
import qrcode
from translations import translations
from tablutil import read_table, template_bytes, TEMPLATE_MIME


def escape_vcard(value):
    """Escape text per RFC 6350 (backslash, comma, semicolon, newline)."""
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace(",", "\\,")
    text = text.replace(";", "\\;")
    text = text.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return text


def build_vcard(name, phone, email, company="", website="", address=""):
    vcard = (
        "BEGIN:VCARD\nVERSION:3.0\n"
        f"FN:{escape_vcard(name)}\n"
        f"TEL;TYPE=CELL:{escape_vcard(phone)}\n"
        f"EMAIL:{escape_vcard(email)}"
    )
    if company:
        vcard += f"\nORG:{escape_vcard(company)}"
    if website:
        vcard += f"\nURL:{escape_vcard(website)}"
    if address:
        vcard += f"\nADR;TYPE=HOME:;;{escape_vcard(address)}"
    vcard += "\nEND:VCARD"
    return vcard


# vCard field -> (translation key, template column).
FIELDS = [
    ("name", "vcard_name", "Full Name"),
    ("phone", "vcard_phone", "Phone"),
    ("email", "vcard_email", "Email"),
    ("company", "vcard_company", "Company"),
    ("website", "vcard_website", "Website"),
    ("address", "vcard_address", "Address"),
]


def run(lang):
    t = translations.get(lang, translations["English"])
    st.markdown(f"<h2 style='text-align:center'>{t['vcard_title']}</h2>", unsafe_allow_html=True)

    mode_map = {t["batch_single"]: "single", t["batch_multi"]: "batch"}
    mode = mode_map[st.radio(t["batch_mode"], list(mode_map.keys()), horizontal=True)]

    if mode == "single":
        name = st.text_input(t["vcard_name"], placeholder="John Doe")
        phone = st.text_input(t["vcard_phone"], placeholder="+123456789")
        email = st.text_input(t["vcard_email"], placeholder="john@example.com")
        company = st.text_input(t["vcard_company"], placeholder="ACME Corp")
        website = st.text_input(t["vcard_website"], placeholder="https://example.com")
        address = st.text_input(t["vcard_address"], placeholder="123 Main St, City, Country")

        if not st.button(t["vcard_button"]):
            return
        if not name or not phone or not email:
            st.warning(t["vcard_required"])
            return
        vcard = build_vcard(name, phone, email, company, website, address)
        st.download_button("⬇️ " + t["vcard_download"], data=vcard.encode("utf-8"),
                           file_name=f"{name.replace(' ', '_')}_contact.vcf", mime="text/vcard")
        qr_buf = BytesIO()
        qrcode.make(vcard).save(qr_buf, format="PNG")
        st.image(qr_buf.getvalue(), caption=t["vcard_qr_caption"], width=200)
        return

    # Batch mode -> one combined .vcf with many cards
    st.download_button(
        "📥 " + t["batch_template"],
        template_bytes([col for _, _, col in FIELDS],
                       [["John Doe", "+123456789", "john@example.com", "ACME", "https://acme.com", "123 Main St"]]),
        file_name="vcard_template.xlsx", mime=TEMPLATE_MIME,
    )
    up = st.file_uploader(t["batch_upload"], type=["csv", "xlsx", "xls"])
    if not up:
        return
    df = read_table(up)
    cols = ["—"] + list(df.columns)
    st.caption(t["batch_name_col"])
    mapping = {}
    grid = st.columns(3)
    for i, (field, key, _) in enumerate(FIELDS):
        default = i + 1 if i < len(df.columns) else 0
        mapping[field] = grid[i % 3].selectbox(t[key], cols, index=default, key=f"vc_{field}")

    if not st.button(t["vcard_button"]):
        return

    def val(row, field):
        c = mapping[field]
        if c == "—" or c not in df.columns:
            return ""
        v = row[c]
        return "" if str(v) == "nan" else str(v).strip()

    cards = []
    for _, row in df.iterrows():
        name = val(row, "name")
        if not name:
            continue
        cards.append(build_vcard(name, val(row, "phone"), val(row, "email"),
                                 val(row, "company"), val(row, "website"), val(row, "address")))
    if not cards:
        st.warning(t["batch_empty"])
        return
    st.success(f"{t['batch_done']}: {len(cards)}")
    st.download_button("⬇️ " + t["vcard_download"], data="\n".join(cards).encode("utf-8"),
                       file_name="contacts.vcf", mime="text/vcard")
