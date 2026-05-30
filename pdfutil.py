"""Shared fpdf2 helper. Lives at repo root (not in services/) so main.py
doesn't treat it as a tool. Registers a Unicode font (DejaVu) when available
so Latin + Cyrillic text renders; CJK glyphs are not covered by DejaVu."""
import os
from fpdf import FPDF

_DEJAVU = {
    "": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "B": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "I": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
}


def make_pdf(orientation="P", fmt="A4", unit="mm"):
    """Return (FPDF, font_family). Uses DejaVu if installed, else Helvetica."""
    pdf = FPDF(orientation=orientation, format=fmt, unit=unit)
    pdf.set_auto_page_break(auto=True, margin=15)
    family = "Helvetica"
    if os.path.exists(_DEJAVU[""]):
        for style, path in _DEJAVU.items():
            if os.path.exists(path):
                pdf.add_font("DejaVu", style, path)
        family = "DejaVu"
    return pdf, family


def pdf_bytes(pdf):
    return bytes(pdf.output())
