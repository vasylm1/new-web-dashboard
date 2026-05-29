import streamlit as st
import os
import importlib.util
from translations import translations

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

# 🌍 Language selector
languages = list(translations.keys())
lang = st.sidebar.selectbox("🌍 Language", languages, index=0)
t = translations[lang]

# 📁 Discover tools in the services directory
services_dir = os.path.join(os.path.dirname(__file__), "services")
os.makedirs(services_dir, exist_ok=True)

tool_files = sorted(f for f in os.listdir(services_dir) if f.endswith(".py"))
# Show friendly names (e.g. "File converter") instead of raw "File converter.py".
display_to_file = {f[:-3]: f for f in tool_files}

selected_display = st.sidebar.selectbox("🧰 " + t["selectTool"], list(display_to_file.keys()))

# 🔍 About section
with st.sidebar.expander(t["aboutTab"], expanded=False):
    st.subheader(t["aboutTitle"])
    for i in range(1, 5):
        st.markdown(f"<p>{t[f'aboutText{i}']}</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <a class="social-link" href="https://www.linkedin.com/in/vasyl-madei-399488247/" target="_blank">
      🔗 {t["linkedinText"]}
    </a>
    """, unsafe_allow_html=True)

# 🔒 Privacy notice (GDPR)
with st.sidebar.expander("🔒 " + t["privacy_title"], expanded=False):
    st.caption(t["privacy_text"])

# 🔧 Load and run the selected tool
st.title("🛠️ My Tools Hub")

selected = display_to_file[selected_display]
file_path = os.path.join(services_dir, selected)
spec = importlib.util.spec_from_file_location("tool_module", file_path)
tool_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool_module)
if hasattr(tool_module, "run"):
    tool_module.run(lang)
