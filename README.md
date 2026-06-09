# 🛠️ My Tools Hub

[![CI](https://github.com/vasylm1/my-tools-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/vasylm1/my-tools-hub/actions/workflows/ci.yml)

A small multilingual web app (Streamlit) bundling everyday utilities. Each tool lives
in its own module under [`services/`](services/) and is auto-discovered by the app.

**Repository:** <https://github.com/vasylm1/my-tools-hub>
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
| Power Automate JSON checker | Highlight JSON syntax errors and validate common Power Automate flow structures |
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
| HTML viewer | Paste or upload HTML and preview it in an isolated responsive frame |
| Text diff | Compare two texts and highlight added/removed lines |
| Social cropper | Crop images to Instagram/Facebook/LinkedIn/X presets |
| Meme generator | Add top/bottom captions to an image |
| Newsletter builder | Build a responsive HTML email newsletter with live preview |
| Roadmap maker | Generate a roadmap/timeline graphic from milestones |
| Sell sheet | Build a product one-pager and export it as HTML |
| Email list validator | Validate, dedupe, and summarize an email column from CSV/Excel |
| Resume builder | Fill a form and export a styled CV as PDF |
| Cover letter | Generate a formatted cover-letter PDF |
| Certificate generator | Create a printable certificate PDF |
| PDF watermark | Stamp diagonal text (e.g. DRAFT) onto every PDF page |
| EPUB builder | Turn Markdown chapters into an EPUB e-book |
| Label sheet | Lay labels out on a printable grid (PDF) |
| Screenshot beautifier | Add a gradient background, padding, rounded corners, and shadow |
| Browser mockup | Wrap a screenshot in a browser-window frame |
| Device mockup | Place a screenshot into a phone or laptop frame |
| Social banner | Generate a LinkedIn/X/Facebook/YouTube banner with name + tagline |
| Certificate image | Create a certificate as a PNG image |

## Self-hosting

**Requirements:** Python **3.11+** (CI runs 3.12; also tested on 3.14) — or just Docker.

### Option A — Python / venv

```bash
git clone https://github.com/vasylm1/my-tools-hub.git
cd my-tools-hub
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

The app opens at <http://localhost:8501>.

### Option B — Docker (recommended)

```bash
git clone https://github.com/vasylm1/my-tools-hub.git
cd my-tools-hub
docker compose up --build -d
```

Then open <http://localhost:8501>. Stop it with `docker compose down`.

The image installs **DejaVu fonts** for the PDF/image tools. For Chinese/Japanese/
Korean text in **PDFs**, add `fonts-noto-cjk` to the `apt-get install` line in the
[`Dockerfile`](Dockerfile). To change the host port, edit the `ports` mapping in
[`docker-compose.yml`](docker-compose.yml) (e.g. `"80:8501"`).

> **TLS, security headers, rate limiting** — only relevant when **self-hosting**.
> Put the container behind a reverse proxy (Nginx/Traefik) that terminates
> HTTPS, adds HSTS/CSP, and rate-limits. Not needed on Streamlit Community Cloud,
> which serves HTTPS for you.

### Streamlit Community Cloud

Point Community Cloud at this repo and `main.py`. It serves HTTPS automatically.
You can't add a reverse proxy or set memory limits there — the platform manages the
runtime (≈1 GB RAM). [`.streamlit/config.toml`](.streamlit/config.toml) still applies:

- Streamlit usage telemetry **disabled** (`gatherUsageStats = false`).
- Upload size capped (`maxUploadSize = 50` MB).
- Tracebacks hidden from users (`showErrorDetails = false`).

### Monitoring

The container exposes Streamlit's health endpoint at `/_stcore/health`. Point an
uptime monitor (e.g. UptimeRobot, Better Uptime) at
`https://<your-app>/_stcore/health` for downtime alerts.

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
