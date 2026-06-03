"""
analyzer.py — Análisis de riesgo de cláusulas con la API de Anthropic.

Recibe list[Clause] del segmenter y devuelve AnalysisResult con un
RiskFinding por cláusula. Cada llamada es independiente; los errores
se aíslan por cláusula sin abortar el análisis completo.

Modelo por defecto: claude-sonnet-4-6 (configurable con ANALYZER_MODEL en .env).
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Callable

from anthropic import Anthropic, APIConnectionError, APITimeoutError, APIStatusError

from segmenter import Clause


# ── Configuración ──────────────────────────────────────────────────────────────

DEFAULT_MODEL = os.getenv("ANALYZER_MODEL", "claude-sonnet-4-6")
MAX_TOKENS    = 512
RETRY_WAIT    = 2.0  # segundos entre reintentos en errores de red

# Lista cerrada según CLAUDE.md — valores en minúsculas
TIPOS_RIESGO: frozenset[str] = frozenset({
    "renovación automática",
    "ajuste de precios",
    "exclusividad",
    "penalidades por incumplimiento o rescisión",
    "plazo de preaviso para cancelar",
    "limitación de responsabilidad",
    "confidencialidad y su duración",
    "jurisdicción y ley aplicable",
    "cesión del contrato a terceros",
    "indemnidad",
})

NIVELES_RIESGO: frozenset[str] = frozenset({"alto", "medio", "bajo"})


# ── Estructuras de datos ───────────────────────────────────────────────────────

@dataclass
class RiskFinding:
    # Cláusula de origen
    numero_clausula:   str
    titulo_clausula:   str
    cuerpo_clausula:   str
    char_start:        int   # posición de inicio de la cláusula en texto_completo
    char_end:          int   # posición de fin
    # Resultado del análisis
    riesgo_detectado:        bool
    tipo_riesgo:             str | None
    nivel_riesgo:            str | None
    explicacion:             str
    cita_textual:            str | None
    requiere_revision_humana: bool
    motivo_revision:         str | None
    # Metadata
    error: str | None = None  # None = análisis exitoso


@dataclass
class AnalysisResult:
    archivo:      str
    analizado_en: str
    modelo:       str
    hallazgos:    list[RiskFinding] = field(default_factory=list)

    @property
    def resumen(self) -> dict:
        con_riesgo = [h for h in self.hallazgos if h.riesgo_detectado]
        por_nivel  = {"alto": 0, "medio": 0, "bajo": 0}
        for h in con_riesgo:
            if h.nivel_riesgo in por_nivel:
                por_nivel[h.nivel_riesgo] += 1
        return {
            "total_clausulas":     len(self.hallazgos),
            "con_riesgo":          len(con_riesgo),
            "requieren_revision":  sum(1 for h in self.hallazgos if h.requiere_revision_humana),
            "errores_de_api":      sum(1 for h in self.hallazgos if h.error),
            "por_nivel":           por_nivel,
        }

    def to_dict(self) -> dict:
        return {
            "archivo":      self.archivo,
            "analizado_en": self.analizado_en,
            "modelo":       self.modelo,
            "resumen":      self.resumen,
            "hallazgos":    [asdict(h) for h in self.hallazgos],
        }


# ── Prompt del sistema ─────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
Sos un asistente especializado en análisis de contratos comerciales con proveedores en Argentina.
Tu tarea es analizar cláusulas individuales e identificar riesgos específicos para la empresa contratante.

TIPOS DE RIESGO A DETECTAR (lista cerrada — usá estos valores exactos):
- renovación automática
- ajuste de precios
- exclusividad
- penalidades por incumplimiento o rescisión
- plazo de preaviso para cancelar
- limitación de responsabilidad
- confidencialidad y su duración
- jurisdicción y ley aplicable
- cesión del contrato a terceros
- indemnidad

REGLAS ESTRICTAS:
1. Si la cláusula no corresponde a ningún tipo de riesgo de la lista, usá riesgo_detectado: false.
2. Usá únicamente los valores de tipo_riesgo de la lista de arriba, en minúsculas exactos.
3. Si detectás riesgo pero no podés determinarlo con certeza, marcá requiere_revision_humana: true.
4. cita_textual debe ser una frase EXACTA del texto de la cláusula. Nunca parafrasees ni inventes.
5. NUNCA incluyas información que no esté en el texto proporcionado.
6. Respondé ÚNICAMENTE con el JSON, sin ningún texto antes ni después.

CRITERIO DE NIVEL DE RIESGO:
- alto: obliga a compromisos significativos, impone costos importantes, o limita derechos de forma relevante
- medio: condición potencialmente desfavorable con alcance limitado o negociable
- bajo: condición estándar de mercado, impacto menor

FORMATO DE RESPUESTA — JSON estricto (sin texto adicional):
{
  "riesgo_detectado": true,
  "tipo_riesgo": "valor exacto de la lista",
  "nivel_riesgo": "alto",
  "explicacion": "1-2 oraciones en español claro, sin tecnicismos legales.",
  "cita_textual": "frase textual exacta de la cláusula",
  "requiere_revision_humana": false,
  "motivo_revision": null
}

Cuando no hay riesgo:
{
  "riesgo_detectado": false,
  "tipo_riesgo": null,
  "nivel_riesgo": null,
  "explicacion": "Breve explicación de por qué no aplica ningún tipo de riesgo.",
  "cita_textual": null,
  "requiere_revision_humana": false,
  "motivo_revision": null
}"""


# ── Función pública ────────────────────────────────────────────────────────────

def analyze_clauses(
    clauses: list[Clause],
    api_key: str,
    *,
    model: str = DEFAULT_MODEL,
    pdf_name: str = "",
    on_progress: Callable[[int, int, str], None] | None = None,
) -> AnalysisResult:
    """
    Analiza cada cláusula con Claude y devuelve un AnalysisResult completo.

    Args:
        clauses:      Lista de cláusulas del segmenter.
        api_key:      API key de Anthropic.
        model:        ID del modelo a usar.
        pdf_name:     Nombre del archivo PDF original (para el JSON de salida).
        on_progress:  Callback opcional con firma (actual, total, nombre_clausula).
    """
    client = Anthropic(api_key=api_key)
    result = AnalysisResult(
        archivo=pdf_name,
        analizado_en=datetime.now().isoformat(timespec="seconds"),
        modelo=model,
    )

    for i, clause in enumerate(clauses, 1):
        if on_progress:
            on_progress(i, len(clauses), clause.titulo or clause.numero)

        finding = _analyze_single(client, clause, model)
        result.hallazgos.append(finding)

    return result


# ── Lógica interna ─────────────────────────────────────────────────────────────

def _analyze_single(client: Anthropic, clause: Clause, model: str) -> RiskFinding:
    """Llama a la API para una cláusula. Reintenta una vez en errores de red
    o JSON malformado. En fallo total devuelve un finding con error marcado."""
    user_prompt = _build_user_prompt(clause)

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw  = response.content[0].text.strip()
            data = _parse_json(raw)

            if data is not None:
                return _build_finding(clause, data)

            # JSON malformado — reintentar una vez
            if attempt == 0:
                continue
            return _error_finding(clause, "La respuesta del modelo no es JSON válido")

        except (APIConnectionError, APITimeoutError) as exc:
            if attempt == 0:
                time.sleep(RETRY_WAIT)
                continue
            return _error_finding(clause, f"Error de conexión: {exc}")

        except APIStatusError as exc:
            # Error del servidor (4xx/5xx): no reintentar
            return _error_finding(clause, f"Error de API ({exc.status_code}): {exc.message}")

    return _error_finding(clause, "Falló tras dos intentos")


def _build_user_prompt(clause: Clause) -> str:
    titulo  = clause.titulo  or "(sin título)"
    cuerpo  = clause.cuerpo  or "(sin cuerpo)"
    return (
        f"Analizá la siguiente cláusula del contrato:\n\n"
        f"Número: {clause.numero}\n"
        f"Título: {titulo}\n\n"
        f"Texto de la cláusula:\n{cuerpo}\n\n"
        f"Respondé únicamente con el JSON."
    )


def _parse_json(raw: str) -> dict | None:
    """Extrae el JSON de la respuesta aunque el modelo agregue texto extra."""
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError:
        return None


def _build_finding(clause: Clause, data: dict) -> RiskFinding:
    """Construye un RiskFinding validando los valores contra las listas cerradas."""
    riesgo   = bool(data.get("riesgo_detectado", False))
    tipo     = (data.get("tipo_riesgo") or "").strip().lower() or None
    nivel    = (data.get("nivel_riesgo") or "").strip().lower() or None
    revision = bool(data.get("requiere_revision_humana", False))

    # Validar contra listas cerradas — si el modelo devolvió algo inválido,
    # marcar para revisión humana en lugar de rechazar silenciosamente.
    if tipo and tipo not in TIPOS_RIESGO:
        tipo = None
        revision = True
        motivo = f"El modelo devolvió un tipo de riesgo no reconocido: '{data.get('tipo_riesgo')}'"
    elif nivel and nivel not in NIVELES_RIESGO:
        nivel = None
        revision = True
        motivo = f"El modelo devolvió un nivel de riesgo no reconocido: '{data.get('nivel_riesgo')}'"
    else:
        motivo = (data.get("motivo_revision") or "").strip() or None

    return RiskFinding(
        numero_clausula          = clause.numero,
        titulo_clausula          = clause.titulo,
        cuerpo_clausula          = clause.cuerpo,
        char_start               = clause.char_start,
        char_end                 = clause.char_end,
        riesgo_detectado         = riesgo,
        tipo_riesgo              = tipo,
        nivel_riesgo             = nivel,
        explicacion              = (data.get("explicacion") or "").strip(),
        cita_textual             = (data.get("cita_textual") or "").strip() or None,
        requiere_revision_humana = revision,
        motivo_revision          = motivo,
        error                    = None,
    )


def _error_finding(clause: Clause, error_msg: str) -> RiskFinding:
    """Crea un finding de error que no pierde la cláusula y pide revisión humana."""
    return RiskFinding(
        numero_clausula          = clause.numero,
        titulo_clausula          = clause.titulo,
        cuerpo_clausula          = clause.cuerpo,
        char_start               = clause.char_start,
        char_end                 = clause.char_end,
        riesgo_detectado         = False,
        tipo_riesgo              = None,
        nivel_riesgo             = None,
        explicacion              = "No se pudo analizar esta cláusula automáticamente.",
        cita_textual             = None,
        requiere_revision_humana = True,
        motivo_revision          = f"Error durante el análisis: {error_msg}",
        error                    = error_msg,
    )
