import React, { useEffect, useRef, useMemo } from 'react'

/**
 * Convierte el texto plano + lista de hallazgos en segmentos renderizables.
 *
 * Defensa aplicada (requisito del CLAUDE.md):
 *  - Ignora hallazgos sin riesgo detectado o sin nivel asignado
 *  - Ignora hallazgos con char_start === 0 AND char_end === 0 (posición no asignada)
 *  - Ignora hallazgos con char_start < 0 o char_end > text.length
 *  - Ignora hallazgos con char_start >= char_end (rango vacío o invertido)
 *  - Omite rangos solapados con el anterior (no rompe el render)
 */
function buildSegments(text, hallazgos) {
  if (!text) return []

  const valid = hallazgos.filter(h => {
    if (!h.riesgo_detectado || !h.nivel_riesgo) return false
    const { char_start: s, char_end: e } = h
    if (s === 0 && e === 0)          return false  // posición no asignada
    if (s < 0 || e > text.length)   return false  // fuera de rango
    if (s >= e)                      return false  // rango vacío o invertido
    return true
  })

  // Ordenar por posición de inicio
  const sorted = [...valid].sort((a, b) => a.char_start - b.char_start)

  const segments = []
  let pos = 0

  for (const h of sorted) {
    const { char_start: s, char_end: e, nivel_riesgo, numero_clausula } = h

    // Saltar si el rango solapa con el bloque anterior
    if (s < pos) continue

    // Texto plano entre el cursor y el inicio de este hallazgo
    if (pos < s) {
      segments.push({ type: 'plain', text: text.slice(pos, s) })
    }

    // Segmento resaltado
    segments.push({ type: 'highlight', text: text.slice(s, e), nivel: nivel_riesgo, id: numero_clausula })
    pos = e
  }

  // Texto plano restante después del último hallazgo
  if (pos < text.length) {
    segments.push({ type: 'plain', text: text.slice(pos) })
  }

  return segments
}

export default function ContractViewer({ text, hallazgos, selectedFinding }) {
  const containerRef = useRef(null)

  // Scroll al hallazgo seleccionado
  useEffect(() => {
    if (!selectedFinding || !containerRef.current) return
    const el = containerRef.current.querySelector(
      `[data-clause-id="${CSS.escape(selectedFinding.numero_clausula)}"]`
    )
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [selectedFinding])

  const segments = useMemo(
    () => buildSegments(text, hallazgos),
    [text, hallazgos]
  )

  return (
    <div className="contract-viewer" ref={containerRef}>
      {segments.map((seg, i) => {
        if (seg.type === 'plain') {
          return <span key={i}>{seg.text}</span>
        }
        const isActive = selectedFinding?.numero_clausula === seg.id
        return (
          <span
            key={i}
            data-clause-id={seg.id}
            className={`hl hl-${seg.nivel}${isActive ? ' hl-active' : ''}`}
          >
            {seg.text}
          </span>
        )
      })}
    </div>
  )
}
