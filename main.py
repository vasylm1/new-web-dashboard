import streamlit as st
import os
import importlib.util
from translations import translations
from views import about, privacy

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
    """Main hub: pick a tool and run it."""
    st.title("🛠️ My Tools Hub")

    services_dir = os.path.join(os.path.dirname(__file__), "services")
    os.makedirs(services_dir, exist_ok=True)

    tool_files = sorted(f for f in os.listdir(services_dir) if f.endswith(".py"))
    # Show friendly names (e.g. "File converter") instead of raw "File converter.py".
    display_to_file = {f[:-3]: f for f in tool_files}

    if not display_to_file:
        st.info("No tools are available yet.")
        return

    selected_display = st.sidebar.selectbox("🧰 " + t["selectTool"], list(display_to_file.keys()))

    selected = display_to_file[selected_display]
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
