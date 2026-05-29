import streamlit as st
from PIL import Image
from io import BytesIO
import qrcode
from translations import translations

def escape_vcard(value):
    """Escape text per RFC 6350 (backslash, comma, semicolon, newline)."""
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace(",", "\\,")
    text = text.replace(";", "\\;")
    text = text.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return text


def run(lang):
    t = translations.get(lang, translations["English"])

    st.markdown(f"<h2 style='text-align:center'>📇 {t['vcard_title']}</h2>", unsafe_allow_html=True)

    name = st.text_input(t["vcard_name"], placeholder="John Doe")
    phone = st.text_input(t["vcard_phone"], placeholder="+123456789")
    email = st.text_input(t["vcard_email"], placeholder="john@example.com")
    company = st.text_input(t["vcard_company"], placeholder="ACME Corp")
    website = st.text_input(t["vcard_website"], placeholder="https://example.com")
    address = st.text_input(t["vcard_address"], placeholder="123 Main St, City, Country")

    if st.button(t["vcard_button"]):
        if not name or not phone or not email:
            st.warning(t["vcard_required"])
            return

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

        # Download button
        st.download_button("⬇️ " + t["vcard_download"], data=vcard.encode("utf-8"), file_name=f"{name.replace(' ', '_')}_contact.vcf", mime="text/vcard")

        # QR code
        qr = qrcode.make(vcard)
        qr_buf = BytesIO()
        qr.save(qr_buf, format="PNG")
        st.image(qr_buf.getvalue(), caption=t["vcard_qr_caption"], width=200)
