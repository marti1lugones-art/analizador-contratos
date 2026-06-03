# Analizador de Contratos con IA

## Qué es
MVP que analiza contratos con proveedores (en español, Argentina).
Sube un PDF y devuelve: cláusulas de riesgo, fechas críticas,
obligaciones de cada parte, y un resumen ejecutivo. Cada hallazgo
cita la cláusula original de donde se extrajo.

## Alcance del MVP (NO agregar nada fuera de esto sin que yo lo pida)
- Solo contratos con proveedores, en español.
- Solo PDFs con texto real (no escaneados / sin OCR todavía).
- Detectar entre 6 y 10 tipos de cláusulas de riesgo predefinidas.
- Sin base de datos vectorial todavía. Pipeline directo de extracción.
- Sin chat libre sobre el contrato (eso es fase 2).

## Stack
- Backend: Python + FastAPI
- Extracción de PDF: PyMuPDF (principal), pdfplumber (respaldo)
- Análisis: API de Anthropic (Claude), salida en JSON estructurado
- Base de datos: PostgreSQL (más adelante; arrancar con archivos locales)
- Frontend: Next.js + React (fase 2 del build)

## Reglas de calidad
- El chunking se hace POR CLÁUSULA respetando la estructura legal
  (artículos, cláusulas, numerales), NUNCA cortando por cantidad de
  caracteres a lo bruto.
- Si el modelo no está seguro de un hallazgo, marcar
  "requiere revisión humana". NUNCA inventar.
- Esto NO es asesoramiento legal. Es una herramienta de asistencia.

## Cláusulas de riesgo a detectar (proveedores)
1. Renovación automática
2. Ajuste / actualización de precios
3. Exclusividad
4. Penalidades por incumplimiento o rescisión
5. Plazo de preaviso para cancelar
6. Limitación de responsabilidad
7. Confidencialidad y su duración
8. Jurisdicción y ley aplicable
9. Cesión del contrato a terceros
10. Indemnidad