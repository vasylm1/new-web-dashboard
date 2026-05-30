import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
from translations import translations
import pandas as pd
import io
import zipfile

_SHEET_FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def _sheet_font(size):
    for p in _SHEET_FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_qr_sheet(qr_images, file_names, cols=3, rows=4):
    """Lay QR codes (with labels) onto A4 pages and return PDF bytes."""
    PW, PH = 1240, 1754  # A4 at ~150 dpi
    margin = 60
    cell_w = (PW - 2 * margin) // cols
    cell_h = (PH - 2 * margin) // rows
    per_page = cols * rows
    font = _sheet_font(22)
    pages = []
    page = None
    for i, (img, name) in enumerate(zip(qr_images, file_names)):
        if i % per_page == 0:
            page = Image.new("RGB", (PW, PH), "white")
        r, c = divmod(i % per_page, cols)
        x = margin + c * cell_w
        y = margin + r * cell_h
        qr_size = min(cell_w, cell_h) - 70
        qr = img.convert("RGB").resize((qr_size, qr_size))
        page.paste(qr, (x + (cell_w - qr_size) // 2, y))
        draw = ImageDraw.Draw(page)
        label = str(name)[:24]
        bbox = draw.textbbox((0, 0), label, font=font)
        draw.text((x + (cell_w - (bbox[2] - bbox[0])) // 2, y + qr_size + 8), label, font=font, fill="black")
        if i % per_page == per_page - 1:
            pages.append(page)
    if page is not None and (page not in pages):
        pages.append(page)
    buf = io.BytesIO()
    pages[0].save(buf, "PDF", save_all=True, append_images=pages[1:])
    return buf.getvalue()

def run(lang):
    t = translations.get(lang, translations["English"])

    st.markdown(f"<h2 style='text-align:center'>{t['title']}</h2>", unsafe_allow_html=True)

    # Mode selection
    mode = st.radio(t["qr_mode"], [t["qr_single"], t["qr_batch"]], horizontal=True)

    if mode == t["qr_single"]:
        run_single_qr(t)
    else:
        run_batch_qr(t)

def run_single_qr(t):
    """Single QR Code generation"""
    text = st.text_input(t["text"], placeholder=t["placeholder"])
    style = st.selectbox(t["style"], ["solid", "gradient"])
    col1, col2 = st.columns(2)
    
    if style == "gradient":
        color1 = col1.color_picker(t["qr_gradient_color1"], "#000000")
        color2 = col2.color_picker(t["qr_gradient_color2"], "#ff0000")
    else:
        color1 = col1.color_picker(t["color1"], "#000000")
        color2 = col2.color_picker(t["color2"], "#000000")

    if st.button(t["button"]):
        if text.strip() == "":
            st.warning("❗ Please enter some text.")
            return

        img = generate_qr_code(text, style, color1, color2)
        st.image(img, caption=t["download"])
        st.download_button(label=t["download"], data=img_to_bytes(img), file_name="qrcode.png", mime="image/png")

def run_batch_qr(t):
    """Batch QR Code generation from Excel file"""
    st.info(t["qr_batch_instructions"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["qr_download_template"]):
            template_df = pd.DataFrame({
                "URL or Text": ["https://example.com", "https://example2.com"],
                "File Name": ["qr_code_1", "qr_code_2"]
            })
            template_bytes = dataframe_to_excel(template_df)
            st.download_button(
                label=t["qr_download_template"],
                data=template_bytes,
                file_name="qr_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    style = st.selectbox(t["style"], ["solid", "gradient"])
    col1, col2 = st.columns(2)
    
    if style == "gradient":
        color1 = col1.color_picker(t["qr_gradient_color1"], "#000000")
        color2 = col2.color_picker(t["qr_gradient_color2"], "#ff0000")
    else:
        color1 = col1.color_picker(t["color1"], "#000000")
        color2 = col2.color_picker(t["color2"], "#000000")
    
    uploaded_file = st.file_uploader(t["qr_upload"], type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file and st.button(t["qr_generate_batch"]):
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Get column names (handle variations)
            cols = df.columns.tolist()
            text_col = cols[0]  # First column for URLs/text
            name_col = cols[1] if len(cols) > 1 else None
            
            qr_images = []
            file_names = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, row in df.iterrows():
                text_value = str(row[text_col]).strip()
                if not text_value or text_value.lower() == 'url or text':
                    continue
                
                # Generate file name
                if name_col and pd.notna(row[name_col]):
                    file_name = str(row[name_col]).strip()
                else:
                    file_name = f"qr_code_{idx + 1}"
                
                # Generate QR code
                img = generate_qr_code(text_value, style, color1, color2)
                qr_images.append(img)
                file_names.append(file_name)
                
                # Update progress
                progress = (idx + 1) / len(df)
                progress_bar.progress(progress)
                status_text.text(f"Generated {idx + 1}/{len(df)} QR codes...")
            
            if qr_images:
                st.success(t["qr_batch_success"])
                
                # Create ZIP file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for img, name in zip(qr_images, file_names):
                        img_bytes = img_to_bytes(img)
                        zip_file.writestr(f"{name}.png", img_bytes)
                
                zip_buffer.seek(0)
                col_zip, col_pdf = st.columns(2)
                col_zip.download_button(
                    label=t["qr_download_all"],
                    data=zip_buffer.getvalue(),
                    file_name="qr_codes.zip",
                    mime="application/zip"
                )
                col_pdf.download_button(
                    label=t["qr_print_sheet"],
                    data=make_qr_sheet(qr_images, file_names),
                    file_name="qr_print_sheet.pdf",
                    mime="application/pdf"
                )

                # Show preview
                st.subheader("Preview")
                preview_cols = st.columns(3)
                for idx, (img, name) in enumerate(zip(qr_images[:9], file_names[:9])):
                    with preview_cols[idx % 3]:
                        st.image(img, caption=name, use_container_width=True)
            else:
                st.warning("No valid data found in the file.")
            
        except Exception as e:
            st.error(f"{t['qr_batch_error']}{str(e)}")

def generate_qr_code(text, style, color1, color2):
    """Generate a QR code with specified style and colors"""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    width, height = img.size

    if style == "gradient":
        gradient = Image.new("RGBA", (width, height), "white")
        draw = ImageDraw.Draw(gradient)
        for y in range(height):
            ratio = y / height
            r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
            g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
            b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # Mask black pixels
        bw = img.convert("L").point(lambda x: 0 if x > 128 else 255)
        img = Image.composite(gradient, Image.new("RGBA", img.size, "white"), bw)

    elif style == "solid":
        r, g, b = tuple(int(color1[i:i + 2], 16) for i in (1, 3, 5))
        solid = Image.new("RGBA", img.size, (r, g, b, 255))
        white = Image.new("RGBA", img.size, "white")
        # Mask: dark QR modules -> use the chosen color, light modules -> white.
        mask = img.convert("L").point(lambda x: 255 if x < 128 else 0)
        img = Image.composite(solid, white, mask)

    return img

def img_to_bytes(img):
    """Convert PIL image to bytes"""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def dataframe_to_excel(df):
    """Convert DataFrame to Excel bytes"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='QR Template', index=False)
    return output.getvalue()
