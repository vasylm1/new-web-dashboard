FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_SERVER_HEADLESS=true

# System deps:
#  - fonts-dejavu-core: DejaVu fonts used by the PDF/image tools (fpdf2 + Pillow).
#  - curl: container healthcheck.
# Optional: add `fonts-noto-cjk` if you need Chinese/Japanese/Korean text in PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        fonts-dejavu-core \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# App source (.dockerignore keeps the image lean).
COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "main.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
