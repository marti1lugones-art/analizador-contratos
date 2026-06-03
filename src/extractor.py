"""
extractor.py — Extracción de texto de PDFs.

Primario: PyMuPDF (fitz).
Fallback automático: pdfplumber si PyMuPDF devuelve texto insuficiente.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF; package name: pymupdf


@dataclass
class ExtractionResult:
    text: str
    page_count: int
    char_count: int
    extractor_used: str  # "pymupdf" | "pdfplumber"


def extract_text(pdf_path: str | Path) -> ExtractionResult:
    """
    Extrae el texto de un PDF.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: si no es PDF o no tiene texto extraíble.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"El archivo no es un PDF: {pdf_path}")

    text, pages = _pymupdf_extract(path)
    extractor = "pymupdf"

    if len(text.strip()) < 100:
        print("  ↩  PyMuPDF devolvió texto insuficiente — reintentando con pdfplumber...")
        text_fb, pages_fb = _pdfplumber_extract(path)
        if len(text_fb.strip()) > len(text.strip()):
            text, pages, extractor = text_fb, pages_fb, "pdfplumber"

    text = _clean_text(text)

    if len(text.strip()) < 100:
        raise ValueError(
            "El PDF no contiene texto extraíble. "
            "¿Es un documento escaneado? El MVP no incluye OCR todavía."
        )

    return ExtractionResult(
        text=text,
        page_count=pages,
        char_count=len(text),
        extractor_used=extractor,
    )


# ── Extractores internos ──────────────────────────────────────────────────────

def _pymupdf_extract(path: Path) -> tuple[str, int]:
    doc = fitz.open(str(path))
    pages_text = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages_text), len(pages_text)


def _pdfplumber_extract(path: Path) -> tuple[str, int]:
    import pdfplumber
    pages_text = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            pages_text.append(page.extract_text() or "")
    return "\n".join(pages_text), len(pages_text)


# ── Limpieza de texto ─────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """
    Normaliza el texto extraído:
    - Une palabras cortadas al final de línea («presta-\nción» → «prestación»)
    - Colapsa secuencias de más de 2 saltos de línea
    - Elimina espacios en blanco al final de cada línea
    """
    # Guión tipográfico al final de línea
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Máximo 2 líneas en blanco consecutivas
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trailing whitespace por línea
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines)
