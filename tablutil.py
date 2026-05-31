"""Small helpers for batch-mode tools: read an uploaded CSV/Excel and build a
downloadable Excel template. Lives at repo root so main.py doesn't list it as a tool."""
import io
import pandas as pd


def read_table(uploaded):
    """Read an uploaded CSV or Excel file into a DataFrame."""
    if uploaded.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded)
    return pd.read_excel(uploaded)


def template_bytes(columns, sample_rows):
    """Return .xlsx bytes for a template with the given columns and example rows."""
    df = pd.DataFrame(sample_rows, columns=columns)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Template")
    return buf.getvalue()


TEMPLATE_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
