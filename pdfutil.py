"""Shared fpdf2 helper. Lives at repo root (not in services/) so main.py
doesn't treat it as a tool. Always registers a Unicode font (DejaVu) so
Latin + Cyrillic text renders; CJK glyphs are not covered by DejaVu.

Font sources (first that exists wins, per style):
  1. system DejaVu (e.g. fonts-dejavu-core in the Docker image)
  2. the DejaVu fonts bundled with matplotlib (always installed — it's a dep)
"""
import os
from fpdf import FPDF

_SYSTEM = {
    "": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "B": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "I": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
}


def _matplotlib_fonts():
    try:
        import matplotlib
        ttf = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
        return {"": os.path.join(ttf, "DejaVuSans.ttf"),
                "B": os.path.join(ttf, "DejaVuSans-Bold.ttf"),
                "I": os.path.join(ttf, "DejaVuSans-Oblique.ttf")}
    except Exception:
        return {}


def _font_paths():
    mpl = _matplotlib_fonts()
    paths = {}
    for style in ("", "B", "I"):
        if os.path.exists(_SYSTEM[style]):
            paths[style] = _SYSTEM[style]
        elif style in mpl and os.path.exists(mpl[style]):
            paths[style] = mpl[style]
    return paths


def make_pdf(orientation="P", fmt="A4", unit="mm"):
    """Return (FPDF, font_family). Uses DejaVu (Unicode) when available, else Helvetica."""
    pdf = FPDF(orientation=orientation, format=fmt, unit=unit)
    pdf.set_auto_page_break(auto=True, margin=15)
    paths = _font_paths()
    if "" in paths:
        for style, path in paths.items():
            pdf.add_font("DejaVu", style, path)
        return pdf, "DejaVu"
    return pdf, "Helvetica"


def pdf_bytes(pdf):
    return bytes(pdf.output())
