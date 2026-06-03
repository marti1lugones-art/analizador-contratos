"""
api.py — Backend FastAPI del analizador de contratos.

Expone POST /analizar: recibe un PDF, corre el pipeline completo
(extracción → segmentación → análisis IA) y devuelve el JSON de hallazgos
más texto_completo para que el frontend pueda resaltar cláusulas.

Arrancar:
    uvicorn src.api:app --reload --port 8000
"""

import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Imports del pipeline — permite ejecutar desde la raíz del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import DEFAULT_MODEL, AnalysisResult, analyze_clauses
from extractor import ExtractionResult, extract_text
from segmenter import segment_clauses

load_dotenv()

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Analizador de Contratos con IA",
    description=(
        "Pipeline de análisis de riesgo para contratos con proveedores argentinos. "
        "Detecta cláusulas de riesgo, niveles de severidad y citas textuales."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir a dominios específicos en producción
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health", summary="Estado del servidor")
def health():
    """Verifica que el servidor está activo y la API key está configurada."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    return {
        "status": "ok",
        "version": "0.1.0",
        "api_key_configurada": bool(api_key),
        "modelo": os.getenv("ANALYZER_MODEL", DEFAULT_MODEL),
    }


@app.post("/analizar", summary="Analizar contrato PDF")
def analizar(file: UploadFile = File(..., description="Archivo PDF del contrato")):
    """
    Recibe un PDF, corre el pipeline completo y devuelve el análisis de riesgo.

    La respuesta incluye:
    - `texto_completo`: texto extraído limpio del PDF
    - `char_start` / `char_end` por hallazgo: posiciones en `texto_completo`
      para que el frontend pueda resaltar la cláusula con `text.slice(start, end)`
    - `advertencia_segmentacion`: presente solo si no se detectó estructura
    """

    # ── Verificar API key antes de procesar ────────────────────────────────────
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "El servidor no tiene API key configurada. "
                "Agregá ANTHROPIC_API_KEY al archivo .env del servidor."
            ),
        )

    # ── Validar que el archivo es un PDF ───────────────────────────────────────
    filename = file.filename or "contrato.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=422,
            detail="El archivo debe ser un PDF (.pdf).",
        )

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=422, detail="El archivo recibido está vacío.")

    # ── Guardar en archivo temporal para el pipeline ───────────────────────────
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # ── 1. Extracción ──────────────────────────────────────────────────────
        try:
            ext: ExtractionResult = extract_text(tmp_path)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        except ValueError as exc:
            # PDF sin texto extraíble, no es PDF, etc.
            raise HTTPException(status_code=422, detail=str(exc))

        # ── 2. Segmentación ────────────────────────────────────────────────────
        clauses, seg_warning = segment_clauses(ext.text)
        # seg_warning no es un error — el pipeline sigue con el texto completo

        # ── 3. Análisis ────────────────────────────────────────────────────────
        model = os.getenv("ANALYZER_MODEL", DEFAULT_MODEL)
        try:
            result: AnalysisResult = analyze_clauses(
                clauses,
                api_key,
                model=model,
                pdf_name=filename,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Error al comunicarse con la API de análisis: {exc}",
            )

        # ── 4. Construir respuesta ─────────────────────────────────────────────
        response = result.to_dict()
        response["texto_completo"] = ext.text

        if seg_warning:
            response["advertencia_segmentacion"] = seg_warning

        return response

    finally:
        # Siempre limpiar el archivo temporal
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
