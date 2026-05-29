# Privacy Notice

_Last updated: 2026-05-29_

This notice explains how **My Tools Hub** handles your data. It is written to align
with the EU General Data Protection Regulation (GDPR).

## What data is processed

The app processes only the content you actively provide to a tool:

- Files you upload (images, PDFs, Office documents, spreadsheets).
- Text you type (URLs, QR content, contact details for vCards).

## How it is processed

- Uploads and entered text are held **in memory** only for as long as needed to
  produce your result (a converted file, QR code, calendar, etc.).
- Results are streamed back to your browser as a download. The app does **not** write
  your content to a database or persistent storage.
- No analytics, advertising, or tracking cookies are used. Streamlit's anonymous usage
  statistics are disabled in `.streamlit/config.toml`.

## Third parties

- **YouTube → Markdown:** when you submit a YouTube URL, the app contacts YouTube to
  retrieve the transcript. This is necessary to deliver the requested feature.
- **PDF → MP3:** the extracted text is sent to Google Text-to-Speech (gTTS) to generate
  the audio.

Only the data required for the selected feature is sent, and only when you trigger it.

## Your rights

Because the app does not retain your content, there is normally nothing stored to
access, correct, or delete after your session ends. If you self-host this app, you are
the data controller and are responsible for your hosting environment (logs, TLS, region).

## Contact

For questions about this notice, contact the operator of the deployment you are using.
