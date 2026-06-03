"""
main.py — CLI del analizador de contratos.

Flujo completo: extracción → segmentación → análisis de riesgo con IA
→ informe por consola → JSON en resultados/.

Uso:
    python src/main.py ruta/al/contrato.pdf
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Permite 'python src/main.py' desde la raíz del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import AnalysisResult, RiskFinding, analyze_clauses, DEFAULT_MODEL
from extractor import extract_text
from segmenter import segment_clauses, detected_pattern_name

LINE_WIDTH   = 62
PREVIEW_LEN  = 160
RESULTS_DIR  = Path(__file__).parent.parent / "resultados"


# ── Iconos por nivel de riesgo ─────────────────────────────────────────────────
LEVEL_ICON = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}
LEVEL_LABEL = {"alto": "RIESGO ALTO", "medio": "RIESGO MEDIO", "bajo": "RIESGO BAJO"}


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Analizador de Contratos con IA — extracción, segmentación y análisis de riesgo"
    )
    parser.add_argument("pdf", help="Ruta al archivo PDF del contrato")
    args = parser.parse_args()

    # ── Verificar API key antes de hacer cualquier otra cosa ──────────────────
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "\n❌  ANTHROPIC_API_KEY no configurada.\n"
            "   Copiá .env.example → .env y agregá tu clave.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    model = os.getenv("ANALYZER_MODEL", DEFAULT_MODEL)

    # ── 1. Extracción ─────────────────────────────────────────────────────────
    print(f"\nExtrayendo texto  →  {args.pdf}")
    try:
        ext = extract_text(args.pdf)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌  {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"  ✓  {ext.page_count} página(s)"
        f"  ·  {ext.char_count:,} caracteres"
        f"  ·  extractor: {ext.extractor_used}"
    )

    # ── 2. Segmentación ───────────────────────────────────────────────────────
    print("\nSegmentando cláusulas...")
    clauses, seg_warning = segment_clauses(ext.text)

    if seg_warning:
        print(f"\n{'═' * LINE_WIDTH}")
        print(f"  {seg_warning}")
        print(f"  Revisá el PDF manualmente antes de continuar.")
        print(f"{'═' * LINE_WIDTH}\n")
    else:
        pattern = detected_pattern_name(ext.text)
        print(f"  ✓  {len(clauses)} cláusula(s)  ·  patrón: {pattern}")

    # ── 3. Análisis de riesgo ─────────────────────────────────────────────────
    print(f"\nAnalizando con {model}...")

    def on_progress(current: int, total: int, nombre: str) -> None:
        label = nombre[:40] + "…" if len(nombre) > 40 else nombre
        print(f"  [{current:02d}/{total:02d}] {label}", flush=True)

    pdf_name = Path(args.pdf).name
    try:
        result = analyze_clauses(
            clauses,
            api_key,
            model=model,
            pdf_name=pdf_name,
            on_progress=on_progress,
        )
    except Exception as e:
        print(f"\n❌  Error inesperado durante el análisis: {e}", file=sys.stderr)
        sys.exit(1)

    # ── 4. Informe por consola ────────────────────────────────────────────────
    _print_report(result, Path(args.pdf).stem)

    # ── 5. Guardar JSON en resultados/ ────────────────────────────────────────
    output_path = _save_results(result)
    print(f"💾  Resultados guardados: {output_path}\n")


# ── Impresión del informe ──────────────────────────────────────────────────────

def _print_report(result: AnalysisResult, titulo: str) -> None:
    res = result.resumen

    print(f"\n{'═' * LINE_WIDTH}")
    print(f"  INFORME DE RIESGO — {titulo[:LINE_WIDTH - 22]}")
    print(
        f"  {res['total_clausulas']} cláusulas"
        f"  ·  {res['con_riesgo']} hallazgos"
        f"  ·  {res['requieren_revision']} para revisar"
    )
    print(f"{'═' * LINE_WIDTH}")

    # Agrupar por nivel de riesgo
    por_nivel: dict[str, list[RiskFinding]] = {"alto": [], "medio": [], "bajo": []}
    sin_riesgo: list[RiskFinding]           = []
    solo_revision: list[RiskFinding]        = []

    for h in result.hallazgos:
        if h.riesgo_detectado and h.nivel_riesgo in por_nivel:
            por_nivel[h.nivel_riesgo].append(h)
        elif h.requiere_revision_humana:
            solo_revision.append(h)
        else:
            sin_riesgo.append(h)

    # Hallazgos por nivel (alto → medio → bajo)
    for nivel in ("alto", "medio", "bajo"):
        hallazgos = por_nivel[nivel]
        icon  = LEVEL_ICON[nivel]
        label = LEVEL_LABEL[nivel]
        print(f"\n{icon}  {label} — {len(hallazgos)} hallazgo(s)")
        if not hallazgos:
            print(f"     (ninguno)")
            continue
        print("─" * LINE_WIDTH)
        for h in hallazgos:
            _print_finding(h)
            # Marcar si también requiere revisión
            if h.requiere_revision_humana:
                print(f"     ⚠  Requiere revisión humana: {h.motivo_revision or ''}")

    # Cláusulas que requieren revisión humana
    # Distinguimos dos casos:
    #   a) Con riesgo detectado + ⚠: ya aparecen listadas en sus grupos arriba
    #   b) Sin riesgo detectado + ⚠: se listan aquí (solo_revision)
    total_revision = res["requieren_revision"]
    en_grupo       = total_revision - len(solo_revision)

    if total_revision == 0:
        print(f"\n⚠   REQUIEREN REVISIÓN HUMANA — ninguna")
    elif not solo_revision:
        # Todas las marcadas ya están visibles en sus grupos con ⚠
        print(
            f"\n⚠   REQUIEREN REVISIÓN HUMANA — "
            f"{en_grupo} marcada(s) con ⚠ dentro de sus grupos de riesgo"
        )
    else:
        # Hay algunas sin nivel asignado que se listan aquí
        header = f"{len(solo_revision)} sin nivel asignado"
        if en_grupo:
            header += f" · {en_grupo} con ⚠ ya listada(s) en sus grupos"
        print(f"\n⚠   REQUIEREN REVISIÓN HUMANA — {header}")
        print("─" * LINE_WIDTH)
        for h in solo_revision:
            num    = h.numero_clausula
            titulo = h.titulo_clausula or "(sin título)"
            motivo = h.motivo_revision or h.error or "Sin motivo especificado"
            print(f"  [{num}] {titulo}")
            print(f"       {motivo}")

    # Sin riesgo identificado
    print(f"\n⚪  SIN RIESGO IDENTIFICADO — {len(sin_riesgo)} cláusula(s)")
    if sin_riesgo:
        nombres = [
            f"[{h.numero_clausula}] {h.titulo_clausula or '(sin título)'}"
            for h in sin_riesgo
        ]
        # Mostrar en líneas de hasta LINE_WIDTH chars
        linea = "  "
        for n in nombres:
            if len(linea) + len(n) + 2 > LINE_WIDTH:
                print(linea)
                linea = "  "
            linea += n + "  "
        if linea.strip():
            print(linea)

    print(f"\n{'─' * LINE_WIDTH}")
    print(f"  Modelo: {result.modelo}  ·  {result.analizado_en}")
    print(f"{'─' * LINE_WIDTH}\n")


def _print_finding(h: RiskFinding) -> None:
    tipo  = (h.tipo_riesgo or "").upper()
    num   = h.numero_clausula
    titulo = h.titulo_clausula or "(sin título)"
    print(f"  [{num}] {tipo} — {titulo}")
    if h.explicacion:
        _print_wrapped(h.explicacion, indent=7)
    if h.cita_textual:
        cita = h.cita_textual[:120] + "…" if len(h.cita_textual) > 120 else h.cita_textual
        print(f"       Cita: \"{cita}\"")


def _print_wrapped(text: str, indent: int = 7) -> None:
    """Imprime texto con salto de línea automático respetando el ancho."""
    prefix = " " * indent
    words  = text.split()
    line   = prefix
    for word in words:
        if len(line) + len(word) + 1 > LINE_WIDTH:
            print(line)
            line = prefix + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)


# ── Guardado de resultados ─────────────────────────────────────────────────────

def _save_results(result: AnalysisResult) -> Path:
    """Guarda el AnalysisResult como JSON en resultados/ y devuelve la ruta."""
    RESULTS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem      = Path(result.archivo).stem or "contrato"
    filename  = f"{stem}_{timestamp}.json"
    out_path  = RESULTS_DIR / filename

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

    return out_path


if __name__ == "__main__":
    main()
