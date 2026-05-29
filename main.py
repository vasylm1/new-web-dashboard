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
    "Excel to calendar": ("cat_data", "ical_title"),
    "Spreadsheet cleaner": ("cat_data", "clean_title"),
    "JSON formatter": ("cat_data", "json_title"),
    "File converter": ("cat_files", "fileconv_title"),
    "Office and YouTube to MD": ("cat_files", "md_title"),
    "Images to PDF": ("cat_files", "img2pdf_title"),
    "Markdown to HTML": ("cat_files", "md2html_title"),
    "Image resizer": ("cat_images", "imgresize_title"),
    "Image watermark": ("cat_images", "wm_title"),
    "Brand palette": ("cat_images", "palette_title"),
}
CATEGORY_ORDER = ["cat_marketing", "cat_data", "cat_files", "cat_images", "cat_other"]

# 🛠 Page configuration
st.set_page_config(page_title="My Tools Hub", page_icon="🛠️", layout="wide")

# 🎨 Embedded styles
st.markdown("""
<style>
:root {
  --primary: #4361ee;
  --accent: #4895ef;
  --secondary: #3f37c9;
}
html, body, [class*="css"] {
  font-family: 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #dfe7f5 100%) !important;
}
.social-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: rgba(67, 97, 238, 0.1);
  border-radius: 8px;
  text-decoration: none;
  color: #4361ee;
  margin-top: 1rem;
  font-weight: bold;
}
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
