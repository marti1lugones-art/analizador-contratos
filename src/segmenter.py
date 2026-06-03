"""
segmenter.py — Segmentación de contratos en cláusulas.

Detecta automáticamente el formato del contrato y divide el texto
respetando la estructura legal. Soporta los 5 patrones más comunes
en contratos argentinos con proveedores.

Regla del CLAUDE.md: el chunking se hace POR CLÁUSULA, NUNCA por
cantidad de caracteres.
"""

import re
from dataclasses import dataclass


@dataclass
class Clause:
    numero: str   # "1", "PRIMERA", "I", etc.
    titulo: str   # texto del encabezado (puede estar vacío)
    cuerpo: str   # cuerpo completo de la cláusula
    char_start: int = 0  # posición de inicio en el texto completo extraído
    char_end:   int = 0  # posición de fin


# ── Patrones de formato legal argentino ──────────────────────────────────────
#
# Orden de precedencia: se elige el que tenga más matches (mínimo 2).
# Cada patrón usa grupos nombrados 'numero' y 'titulo'.

_ORDINALES = (
    r"PRIMERA?|SEGUNDA?|TERCERA?|CUARTA?|QUINTA?|SEXTA?"
    r"|S[EÉ]PTIMA?|OCTAVA?|NOVENA?"
    # Formas latinas para 11° y 12° (undécima, duodécima)
    r"|UND[EÉ]CIMA?"
    r"|DUOD[EÉ]CIMA?"
    # Formas compuestas ANTES de la simple: DECIMOPRIMERA debe tener precedencia
    # sobre D[EÉ]CIMA? para que el motor no se detenga en "DECIM" (A?=0)
    r"|D[EÉ]CIMO(?:PRIMERA?|SEGUNDA?|TERCERA?|CUARTA?|QUINTA?"
    r"|SEXTA?|S[EÉ]PTIMA?|OCTAVA?|NOVENA?)?"
    # Forma simple DÉCIMA después de las compuestas
    r"|D[EÉ]CIMA?"
    r"|VIG[EÉ]SIMA?(?:\s+\w+)?"
    r"|TRIG[EÉ]SIMA?(?:\s+\w+)?"
)

_PATTERNS: dict[str, re.Pattern] = {
    # CLÁUSULA PRIMERA: OBJETO   /   CLAUSULA SEGUNDA — PRECIO
    "clausula_ordinal": re.compile(
        rf"^(?:CL[ÁA]USULA|ART[ÍI]CULO)\s+(?P<numero>{_ORDINALES})\s*[:\.\-]?\s*(?P<titulo>[^\n]*)",
        re.MULTILINE | re.IGNORECASE,
    ),
    # ARTÍCULO 3°: VIGENCIA   /   ARTICULO 5. RESPONSABILIDAD
    "articulo_numerado": re.compile(
        r"^(?:ART[ÍI]CULO)\s+(?P<numero>\d+)[°º]?\s*[:\.\-]\s*(?P<titulo>[^\n]*)",
        re.MULTILINE | re.IGNORECASE,
    ),
    # 1.- OBJETO DEL CONTRATO    (formato muy común en AR)
    "num_guion": re.compile(
        r"^(?P<numero>\d+)\s*\.-\s*(?P<titulo>[^\n]*)",
        re.MULTILINE,
    ),
    # 1. OBJETO DEL CONTRATO   (título en mayúsculas, al menos 4 chars)
    "num_punto_mayus": re.compile(
        r"^(?P<numero>\d+)\.\s+(?P<titulo>[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\(\)/]{3,})",
        re.MULTILINE,
    ),
    # I. OBJETO   /   II. PRECIO   (numerales romanos)
    "romano": re.compile(
        r"^(?P<numero>X{0,2}(?:IX|IV|VI{0,3}|I{1,3}))\.\s+(?P<titulo>[^\n]+)",
        re.MULTILINE,
    ),
}


def segment_clauses(text: str) -> tuple[list[Clause], str | None]:
    """
    Segmenta el texto en cláusulas detectando el patrón dominante.

    Retorna:
        (clauses, warning)
        - warning es None si la segmentación fue exitosa
        - warning es un string descriptivo si se usó el fallback
    """
    pattern_name, pattern = _detect_dominant_pattern(text)

    if pattern is None:
        return _fallback(text), "⚠  No se detectó estructura de cláusulas — revisar manualmente"

    clauses = _split_by_pattern(text, pattern)

    if not clauses:
        return _fallback(text), "⚠  No se detectó estructura de cláusulas — revisar manualmente"

    return clauses, None


def detected_pattern_name(text: str) -> str | None:
    """Devuelve el nombre del patrón detectado, útil para logging."""
    name, _ = _detect_dominant_pattern(text)
    return name


# ── Lógica interna ────────────────────────────────────────────────────────────

def _detect_dominant_pattern(text: str) -> tuple[str | None, re.Pattern | None]:
    """Elige el patrón con más coincidencias. Requiere mínimo 2 matches."""
    best_name: str | None = None
    best_pattern: re.Pattern | None = None
    best_count = 1  # umbral mínimo: debe superar 1 para ser considerado

    for name, pattern in _PATTERNS.items():
        count = len(pattern.findall(text))
        if count > best_count:
            best_count = count
            best_name = name
            best_pattern = pattern

    return best_name, best_pattern


def _split_by_pattern(text: str, pattern: re.Pattern) -> list[Clause]:
    """Divide el texto en chunks usando las posiciones de cada match."""
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    clauses = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end]

        # La primera línea es el encabezado; el resto es el cuerpo
        first_nl = chunk.find("\n")
        cuerpo = chunk[first_nl:].strip() if first_nl != -1 else ""

        numero = _group(match, "numero")
        titulo = _clean_title(_group(match, "titulo"))

        clauses.append(Clause(
            numero=numero, titulo=titulo, cuerpo=cuerpo,
            char_start=start, char_end=end,
        ))

    return clauses


def _fallback(text: str) -> list[Clause]:
    """Devuelve el texto completo como una única cláusula."""
    return [Clause(
        numero="—", titulo="Texto completo del contrato", cuerpo=text.strip(),
        char_start=0, char_end=len(text),
    )]


def _group(match: re.Match, name: str) -> str:
    """Extrae un grupo nombrado del match sin lanzar excepción."""
    try:
        val = match.group(name)
        return val.strip() if val else ""
    except IndexError:
        return ""


def _clean_title(title: str) -> str:
    """Strip, colapsa espacios internos, quita puntuación final."""
    title = " ".join(title.split())
    title = title.rstrip(".:- ")
    return title
