# 🛠️ My Tools Hub

A small multilingual web app (Streamlit) bundling everyday utilities. Each tool lives
in its own module under [`services/`](services/) and is auto-discovered by the app.

**Languages:** English · Polski · Deutsch · Українська · 中文

## Tools

| Tool | What it does |
|------|--------------|
| File converter | Convert between image formats (PNG/JPG/WEBP/BMP/TIFF) and turn a PDF into an MP3 (text-to-speech) |
| QR code | Generate single or batch QR codes (solid or gradient style) from text/URLs or an Excel/CSV file |
| Excel to calendar | Convert an Excel sheet of events into an `.ics` calendar file |
| Office and YouTube to MD | Convert Office/PDF/EPub/HTML documents — or a YouTube transcript — to Markdown |
| Vcard generator | Build a `.vcf` contact card plus a QR code |
| Email signature | Build a self-contained HTML email signature (photo, colors, social links) with live preview, copy, and download |
| Image resizer | Resize & compress images (PNG/JPEG/WEBP) or generate a favicon pack (PNG sizes + `.ico`) |
| Hashtag extractor | Pull top keywords and suggested/found hashtags from a block of text |
| Spreadsheet cleaner | Trim, dedupe, drop empty rows/cols, and standardize headers in CSV/Excel |
| JSON formatter | Format, minify, validate JSON, or convert an array of objects to CSV |
| Images to PDF | Combine multiple images into a single PDF (A4/Letter/fit, portrait/landscape) |
| Markdown to HTML | Render Markdown to styled, self-contained HTML with preview and download |
| Image watermark | Overlay text or a logo watermark on an image (position, opacity, size) |
| Brand palette | Extract a dominant color palette (HEX) from an image and export as CSS |
| Copy analyzer | Word/char/sentence counts, reading time, and Flesch readability for copy |
| Headline analyzer | Score a headline on length, power words, and numbers with SEO length hints |
| Persona builder | Build a persona/ICP one-pager and export it as HTML |
| Chart maker | Turn a CSV/Excel column into a bar/line/pie chart (PNG) |
| Datetime toolkit | Date difference, workdays-between, and timezone conversion |
| Unit converter | Convert length, mass, temperature, and data units |
| SQL formatter | Pretty-print and standardize SQL queries |
| Data anonymizer | Mask emails/phones and hash a chosen column in CSV/Excel |
| Fake data generator | Generate locale-aware sample data (name/email/company…) as CSV |
| Currency converter | Convert between currencies using live rates (open.er-api.com) |
| PDF to text | Extract selectable text from a PDF |
| HTML to Markdown | Convert pasted HTML into Markdown |
| Text diff | Compare two texts and highlight added/removed lines |
| Social cropper | Crop images to Instagram/Facebook/LinkedIn/X presets |
| Meme generator | Add top/bottom captions to an image |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

The app opens at <http://localhost:8501>.

## Deployment

Production settings live in [`.streamlit/config.toml`](.streamlit/config.toml):

- Streamlit usage telemetry is **disabled** (`gatherUsageStats = false`).
- Upload size is capped (`maxUploadSize = 50` MB).
- Python tracebacks are hidden from end users (`showErrorDetails = false`).

Deploy on any container/PaaS host. For an EU audience, choose an EU region and
serve over HTTPS (most platforms terminate TLS for you).

## Privacy (GDPR)

- Uploaded files are processed **in memory** to perform the conversion and are **not
  stored** on a server or shared with third parties.
- No analytics or tracking cookies are used; Streamlit's own telemetry is disabled.
- The *Office and YouTube to MD* tool sends the YouTube URL to YouTube to fetch the
  transcript — that request leaves the app by design.

See [PRIVACY.md](PRIVACY.md) for the full notice.

## Adding a tool

Drop a `your_tool.py` file in [`services/`](services/) exposing a `run(lang)` function.
It will appear automatically in the sidebar. Use `translations.get(lang, translations["English"])`
for any user-facing text.
