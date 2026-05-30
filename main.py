import streamlit as st
import os
import importlib.util
from collections import defaultdict
from translations import translations
from views import about, privacy

# Tool registry: service filename (without .py) -> (category key, title-translation key).
# The title key reuses each tool's own translated title, so tool names are localized.
TOOL_REGISTRY = {
    "QR code": ("cat_marketing", "title"),
    "Vcard generator": ("cat_marketing", "vcard_title"),
    "Email signature": ("cat_marketing", "email_signature_title"),
    "Hashtag extractor": ("cat_marketing", "kw_title"),
    "Copy analyzer": ("cat_marketing", "copyan_title"),
    "Headline analyzer": ("cat_marketing", "head_title"),
    "Persona builder": ("cat_marketing", "persona_title"),
    "Newsletter builder": ("cat_marketing", "news_title"),
    "Roadmap maker": ("cat_marketing", "road_title"),
    "Sell sheet": ("cat_marketing", "sell_title"),
    "Excel to calendar": ("cat_data", "ical_title"),
    "Spreadsheet cleaner": ("cat_data", "clean_title"),
    "JSON formatter": ("cat_data", "json_title"),
    "Chart maker": ("cat_data", "chart_title"),
    "Datetime toolkit": ("cat_data", "dt_title"),
    "Unit converter": ("cat_data", "unit_title"),
    "SQL formatter": ("cat_data", "sql_title"),
    "Data anonymizer": ("cat_data", "anon_title"),
    "Fake data generator": ("cat_data", "faker_title"),
    "Currency converter": ("cat_data", "cur_title"),
    "Email list validator": ("cat_data", "elv_title"),
    "File converter": ("cat_files", "fileconv_title"),
    "Office and YouTube to MD": ("cat_files", "md_title"),
    "Images to PDF": ("cat_files", "img2pdf_title"),
    "Markdown to HTML": ("cat_files", "md2html_title"),
    "PDF to text": ("cat_files", "pdftxt_title"),
    "HTML to Markdown": ("cat_files", "html2md_title"),
    "Text diff": ("cat_files", "diff_title"),
    "Resume builder": ("cat_files", "cv_title"),
    "Cover letter": ("cat_files", "cl_title"),
    "Certificate generator": ("cat_files", "cert_title"),
    "PDF watermark": ("cat_files", "pdfwm_title"),
    "EPUB builder": ("cat_files", "epub_title"),
    "Label sheet": ("cat_files", "label_title"),
    "Image resizer": ("cat_images", "imgresize_title"),
    "Image watermark": ("cat_images", "wm_title"),
    "Brand palette": ("cat_images", "palette_title"),
    "Social cropper": ("cat_images", "crop_title"),
    "Meme generator": ("cat_images", "meme_title"),
    "Screenshot beautifier": ("cat_images", "beaut_title"),
    "Browser mockup": ("cat_images", "brow_title"),
    "Device mockup": ("cat_images", "dev_title"),
    "Social banner": ("cat_images", "sb_title"),
    "Certificate image": ("cat_images", "certimg_title"),
}
CATEGORY_ORDER = ["cat_marketing", "cat_data", "cat_files", "cat_images", "cat_other"]

# 🛠 Page configuration
st.set_page_config(page_title="My Tools Hub", page_icon="🛠️", layout="wide")

# 🎨 Embedded styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root { --primary:#4361ee; --accent:#4895ef; --secondary:#3a0ca3; --ink:#0f172a; --line:#e8edf5; }

html, body, [class*="css"], .stApp { font-family:'Inter','Segoe UI',sans-serif; }
.stApp { background:#f7f9fc; }

/* Headings */
h1, h2, h3 { color:var(--ink); letter-spacing:-0.015em; font-weight:700; }
h1 { font-weight:800; }

/* Sidebar */
[data-testid="stSidebar"] { background:#ffffff; border-right:1px solid var(--line); }
[data-testid="stSidebar"] label { font-weight:600; }

/* Primary + download buttons */
.stButton > button, [data-testid="stDownloadButton"] > button {
  border-radius:10px; border:1px solid transparent; font-weight:600; color:#fff;
  background:linear-gradient(135deg, var(--primary), var(--accent));
  box-shadow:0 1px 2px rgba(67,97,238,.25);
  transition:transform .12s ease, box-shadow .12s ease, filter .12s ease;
}
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
  transform:translateY(-1px); filter:brightness(1.05); color:#fff;
  box-shadow:0 6px 16px rgba(67,97,238,.28);
}

/* Rounded inputs */
[data-baseweb="input"], [data-baseweb="select"] > div, .stTextArea textarea { border-radius:10px !important; }

/* Metrics as cards */
[data-testid="stMetric"] {
  background:#fff; border:1px solid var(--line); border-radius:14px;
  padding:14px 16px; box-shadow:0 1px 2px rgba(16,24,40,.04);
}

/* Rounded tables & code blocks */
[data-testid="stDataFrame"], pre { border-radius:12px; overflow:hidden; }

.social-link {
  display:inline-block; padding:.55rem 1.1rem; background:rgba(67,97,238,.10);
  border-radius:10px; text-decoration:none; color:var(--primary);
  margin-top:1rem; font-weight:600; transition:background .15s ease;
}
.social-link:hover { background:rgba(67,97,238,.18); }
</style>
""", unsafe_allow_html=True)

# 🌍 Language selector — shared across every page
languages = list(translations.keys())
lang = st.sidebar.selectbox("🌍 Language", languages, index=0)
t = translations[lang]


def tools_page():
    """Main hub: pick a category, then a tool, and run it."""
    st.title("🛠️ My Tools Hub")

    services_dir = os.path.join(os.path.dirname(__file__), "services")
    os.makedirs(services_dir, exist_ok=True)

    tool_files = sorted(f for f in os.listdir(services_dir) if f.endswith(".py"))
    if not tool_files:
        st.info("No tools are available yet.")
        return

    # Group tools by category; each entry is (localized_label, filename).
    groups = defaultdict(list)
    for fname in tool_files:
        name = fname[:-3]
        cat_key, title_key = TOOL_REGISTRY.get(name, ("cat_other", None))
        label = t.get(title_key, name) if title_key else name
        groups[cat_key].append((label, fname))

    categories = [c for c in CATEGORY_ORDER if c in groups]
    categories += [c for c in groups if c not in categories]

    cat_key = st.sidebar.selectbox(
        "🗂️ " + t["category"], categories, format_func=lambda c: t.get(c, c)
    )
    tools_in_cat = sorted(groups[cat_key])
    label_to_file = dict(tools_in_cat)
    chosen_label = st.sidebar.selectbox("🧰 " + t["selectTool"], list(label_to_file.keys()))

    selected = label_to_file[chosen_label]
    file_path = os.path.join(services_dir, selected)
    spec = importlib.util.spec_from_file_location("tool_module", file_path)
    tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool_module)
    if hasattr(tool_module, "run"):
        tool_module.run(lang)


# 🧭 Multipage navigation
pages = [
    st.Page(tools_page, title=t["nav_tools"], icon="🧰", default=True),
    st.Page(lambda: about.render(t), title=t["nav_about"], icon="👤", url_path="about"),
    st.Page(lambda: privacy.render(t), title=t["nav_privacy"], icon="🔒", url_path="privacy"),
]
st.navigation(pages).run()
