import streamlit as st
import os
import re
import html
import importlib.util
from collections import defaultdict
from urllib.parse import quote
from translations import translations
from views import about, privacy, imprint

REPO_URL = "https://github.com/vasylm1/my-tools-hub"

# Accent color per category (used for the card left-border).
CAT_COLORS = {
    "cat_marketing": "#4361ee", "cat_data": "#0ea5e9", "cat_files": "#8b5cf6",
    "cat_images": "#ec4899", "cat_other": "#64748b",
}
_EMOJI = re.compile(r'[\U0001F000-\U0001FAFF←-⇿⌀-➿⬀-⯿☀-⛿][️‍⃣]?\s*')


def _noemoji(text):
    return _EMOJI.sub("", text).strip()

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
    "Power Automate JSON checker": ("cat_data", "paj_title"),
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
    "HTML viewer": ("cat_files", "htmlview_title"),
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

# Tool groups: one card opens a page that switches between the member tools.
# id -> (category, group-title key, [member service filenames])
TOOL_GROUPS = {
    "pdf": ("cat_files", "group_pdf", ["PDF to text.py", "PDF watermark.py", "Images to PDF.py"]),
    "md": ("cat_files", "group_md", ["Markdown to HTML.py", "HTML to Markdown.py"]),
    "cert": ("cat_files", "group_cert", ["Certificate generator.py", "Certificate image.py"]),
    "mockup": ("cat_images", "group_mockup", ["Screenshot beautifier.py", "Browser mockup.py", "Device mockup.py"]),
}
GROUPED_FILES = {f for _, _, members in TOOL_GROUPS.values() for f in members}

# 🛠 Page configuration
st.set_page_config(page_title="My Tools Hub", page_icon="🛠️", layout="wide")

# 🎨 Embedded styles
st.markdown("""
<style>
:root { --primary:#4f46e5; --accent:#6366f1; --ink:#0f172a; --muted:#64748b; --line:#e9edf4; --bg:#f6f7fb; }

html, body, [class*="css"], .stApp {
  font-family:Aptos,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  color:var(--ink);
}
.stApp { background:var(--bg); }

/* Hide Streamlit chrome for an app-like shell */
#MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"], footer { display:none !important; }
[data-testid="stHeader"] { background:transparent; height:0; }

/* Center & constrain content */
.block-container { max-width:1160px; padding-top:2.2rem; padding-bottom:4rem; }

/* Typography */
h1, h2, h3 { color:var(--ink); letter-spacing:-0.02em; font-weight:700; }
h1 { font-weight:800; }

/* Sidebar */
[data-testid="stSidebar"] { background:#ffffff; border-right:1px solid var(--line); }
[data-testid="stSidebar"] label { font-weight:600; color:var(--ink); }
[data-testid="stSidebarNav"] { padding-top:.5rem; }

/* Buttons */
.stButton > button, [data-testid="stDownloadButton"] > button {
  border-radius:11px; border:1px solid transparent; font-weight:600; color:#fff; padding:.5rem 1.05rem;
  background:linear-gradient(135deg, var(--primary), var(--accent));
  box-shadow:0 1px 2px rgba(79,70,229,.20);
  transition:transform .12s ease, box-shadow .12s ease, filter .12s ease;
}
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
  transform:translateY(-1px); filter:brightness(1.06); color:#fff;
  box-shadow:0 8px 20px rgba(79,70,229,.26);
}

/* Inputs */
[data-baseweb="input"], [data-baseweb="select"] > div, .stTextArea textarea, [data-baseweb="base-input"] {
  border-radius:11px !important;
}
[data-testid="stTextInput"] input { padding:.6rem .9rem; }

/* Metrics as cards */
[data-testid="stMetric"] {
  background:#fff; border:1px solid var(--line); border-radius:16px;
  padding:16px 18px; box-shadow:0 1px 2px rgba(16,24,40,.04);
}

/* Rounded tables & code blocks */
[data-testid="stDataFrame"], pre { border-radius:14px; overflow:hidden; border:1px solid var(--line); }

.social-link {
  display:inline-block; padding:.6rem 1.2rem; background:rgba(79,70,229,.10);
  border-radius:11px; text-decoration:none; color:var(--primary);
  margin-top:1rem; font-weight:600; transition:background .15s ease;
}
.social-link:hover { background:rgba(79,70,229,.18); }

/* ---------- Landing ---------- */
.hero { padding:4px 0 22px; border-bottom:1px solid var(--line); margin-bottom:18px; }
.hero h1 { font-size:2.3rem; margin:0 0 6px;
  background:linear-gradient(90deg,#1e1b4b,#4f46e5); -webkit-background-clip:text;
  background-clip:text; -webkit-text-fill-color:transparent; }
.hero p { color:var(--muted); margin:0; font-size:1.05rem; }

.cat-head { display:flex; align-items:center; gap:8px; font-size:.74rem; text-transform:uppercase;
  letter-spacing:.08em; color:var(--muted); font-weight:700; margin:26px 0 10px; }
.cat-head::before { content:""; width:9px; height:9px; border-radius:3px; background:var(--cat,#4f46e5); }

.tool-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(248px,1fr)); gap:14px; }
.tool-card { display:flex; align-items:center; gap:13px; padding:14px 16px;
  background:#fff; border:1px solid var(--line); border-radius:16px;
  box-shadow:0 1px 2px rgba(16,24,40,.04);
  transition:transform .14s ease, box-shadow .14s ease, border-color .14s ease; }
.tool-card:hover { transform:translateY(-2px); border-color:var(--cat,#4f46e5);
  box-shadow:0 12px 26px rgba(16,24,40,.10); }
.tc-badge { flex:0 0 auto; width:44px; height:44px; border-radius:12px; color:#fff;
  display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.1rem;
  background:var(--cat,#4f46e5); }
.tc-name { color:var(--ink); font-weight:650; font-size:.98rem; line-height:1.22; }
/* Kill Streamlit's link underline/colour inside cards */
.tool-card, .tool-card:hover, .tool-card *, .tc-name, .tc-badge { text-decoration:none !important; }
.tc-group .tc-name { flex:1; }
.tc-group::after { content:"›"; color:#cbd5e1; font-size:1.5rem; line-height:1; padding-left:6px; }

.back-link { display:inline-block; margin-bottom:10px; color:var(--primary);
  text-decoration:none !important; font-weight:600; }
.back-link:hover { opacity:.8; }
</style>
""", unsafe_allow_html=True)

# 🌍 Language selector — shared across every page
languages = list(translations.keys())
lang = st.sidebar.selectbox("🌍 Language", languages, index=0)
st.sidebar.markdown(f"<a href='{REPO_URL}' target='_blank' style='font-size:.85rem;color:#64748b;text-decoration:none;'>↗ GitHub</a>", unsafe_allow_html=True)
# Merge over English so any key missing in the selected language never crashes.
t = {**translations.get("English", {}), **translations.get(lang, {})}

# Safe defaults for this file's own UI strings (resilient to a partial deploy).
_UI_DEFAULTS = {
    "nav_tools": "Tools", "nav_about": "About", "nav_privacy": "Privacy", "nav_imprint": "Imprint",
    "back_to_tools": "All tools", "tools_tagline": "Your toolkit for everyday tasks",
    "tools_word": "tools", "tools_search": "Search tools…", "tools_none": "No tools match your search.",
    "cat_marketing": "Marketing", "cat_data": "Data", "cat_files": "Files",
    "cat_images": "Images", "cat_other": "Other", "cat_all": "All",
    "group_pdf": "PDF Tools", "group_md": "Markdown ↔ HTML",
    "group_cert": "Certificate Maker", "group_mockup": "Mockups",
}


def ui(key):
    return t.get(key) or _UI_DEFAULTS.get(key, key)


def _run_tool(filename):
    services_dir = os.path.join(os.path.dirname(__file__), "services")
    file_path = os.path.join(services_dir, filename)
    spec = importlib.util.spec_from_file_location("tool_module", file_path)
    tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool_module)
    if hasattr(tool_module, "run"):
        tool_module.run(lang)


def _member_label(fname):
    _, title_key = TOOL_REGISTRY.get(fname[:-3], ("cat_other", None))
    return t.get(title_key, fname[:-3]) if title_key else fname[:-3]


def _run_group(gid):
    """Render a group page: a switcher across member tools; run the chosen one."""
    _, _, members = TOOL_GROUPS[gid]
    label_to_file = {_member_label(f): f for f in members}
    labels = list(label_to_file.keys())
    st.markdown(f"### {html.escape(ui('group_' + gid))}")
    seg = getattr(st, "segmented_control", None)
    if seg is not None:
        choice = seg("tools", labels, default=labels[0], label_visibility="collapsed")
    else:
        choice = st.radio("tools", labels, horizontal=True, label_visibility="collapsed")
    choice = choice or labels[0]
    st.divider()
    _run_tool(label_to_file[choice])


def tools_page():
    """Searchable card grid: pick a tool or group to open it (?tool=<id>)."""
    services_dir = os.path.join(os.path.dirname(__file__), "services")
    os.makedirs(services_dir, exist_ok=True)
    by_id = {f[:-3]: f for f in sorted(os.listdir(services_dir)) if f.endswith(".py")}

    active = st.query_params.get("tool")
    # A group page
    if active and active.startswith("group:") and active[6:] in TOOL_GROUPS:
        st.markdown(f'<a class="back-link" href="?" target="_self">← {html.escape(ui("back_to_tools"))}</a>',
                    unsafe_allow_html=True)
        _run_group(active[6:])
        return
    # A single tool
    if active in by_id:
        st.markdown(f'<a class="back-link" href="?" target="_self">← {html.escape(ui("back_to_tools"))}</a>',
                    unsafe_allow_html=True)
        _run_tool(by_id[active])
        return

    # Landing: hero + search + category filter + grid.
    st.markdown(
        f'<div class="hero"><h1>My Tools Hub</h1>'
        f'<p>{html.escape(ui("tools_tagline"))} · {len(by_id)} {html.escape(ui("tools_word"))}</p></div>',
        unsafe_allow_html=True,
    )

    # Categories that actually contain tools (for the filter).
    present = {cat for cat, _, _ in TOOL_GROUPS.values()}
    for fid, fname in by_id.items():
        if fname not in GROUPED_FILES:
            present.add(TOOL_REGISTRY.get(fid, ("cat_other", None))[0])
    ordered = [c for c in CATEGORY_ORDER if c in present] + [c for c in present if c not in CATEGORY_ORDER]

    query = st.text_input("search", placeholder="🔍  " + ui("tools_search"), label_visibility="collapsed").strip().lower()
    all_label = ui("cat_all")
    label_to_cat = {_noemoji(ui(c)): c for c in ordered}
    options = [all_label] + list(label_to_cat.keys())
    seg = getattr(st, "segmented_control", None)
    if seg is not None:
        chosen = seg("filter", options, default=all_label, label_visibility="collapsed")
    else:
        chosen = st.radio("filter", options, horizontal=True, label_visibility="collapsed")
    sel_cat = label_to_cat.get(chosen) if (chosen and chosen != all_label) else None

    # Entries per category: (label, href_id). Groups first, then ungrouped tools.
    by_cat = defaultdict(list)
    for gid, (cat_key, _, members) in TOOL_GROUPS.items():
        label = ui("group_" + gid)
        haystack = (label + " " + " ".join(_member_label(m) for m in members)).lower()
        if query and query not in haystack:
            continue
        by_cat[cat_key].append((label, "group:" + gid))
    for fid, fname in by_id.items():
        if fname in GROUPED_FILES:
            continue
        cat_key, title_key = TOOL_REGISTRY.get(fid, ("cat_other", None))
        label = t.get(title_key, fid) if title_key else fid
        if query and query not in label.lower():
            continue
        by_cat[cat_key].append((label, fid))

    categories = [c for c in CATEGORY_ORDER if c in by_cat] + [c for c in by_cat if c not in CATEGORY_ORDER]
    if sel_cat is not None:
        categories = [c for c in categories if c == sel_cat]
    if not categories:
        st.info(ui("tools_none"))
        return

    for cat in categories:
        color = CAT_COLORS.get(cat, "#4f46e5")
        cat_label = html.escape(_noemoji(ui(cat)))
        cards = ""
        for label, href_id in sorted(by_cat[cat]):
            badge = html.escape((label.strip()[:1] or "•").upper())
            grp = " tc-group" if href_id.startswith("group:") else ""
            cards += (
                f'<a class="tool-card{grp}" style="--cat:{color}" href="?tool={quote(href_id)}" target="_self">'
                f'<span class="tc-badge">{badge}</span>'
                f'<span class="tc-name">{html.escape(label)}</span></a>'
            )
        st.markdown(f'<div class="cat-head" style="--cat:{color}">{cat_label}</div>'
                    f'<div class="tool-grid">{cards}</div>', unsafe_allow_html=True)


# 🧭 Multipage navigation
pages = [
    st.Page(tools_page, title=ui("nav_tools"), icon="🧰", default=True),
    st.Page(lambda: about.render(t), title=ui("nav_about"), icon="👤", url_path="about"),
    st.Page(lambda: privacy.render(t), title=ui("nav_privacy"), icon="🔒", url_path="privacy"),
    st.Page(lambda: imprint.render(t), title=ui("nav_imprint"), icon="⚖️", url_path="imprint"),
]
st.navigation(pages).run()
