import React, { useMemo } from 'react'

const NIVEL_CONFIG = {
  alto:  { icon: '🔴', label: 'ALTO',  badge: 'badge-alto'  },
  medio: { icon: '🟡', label: 'MEDIO', badge: 'badge-medio' },
  bajo:  { icon: '🟢', label: 'BAJO',  badge: 'badge-bajo'  },
}

// ── Tarjeta individual ───────────────────────────────────────────────────────

function FindingCard({ h, isSelected, onClick }) {
  const cfg = NIVEL_CONFIG[h.nivel_riesgo]
  return (
    <button
      type="button"
      className={[
        'finding-card',
        h.nivel_riesgo ? `finding-card-${h.nivel_riesgo}` : '',
        isSelected ? 'finding-card-active' : '',
      ].filter(Boolean).join(' ')}
      onClick={onClick}
    >
      <div className="finding-card-top">
        <span className="finding-clause-id">[{h.numero_clausula}]</span>
        <span className="finding-clause-title">{h.titulo_clausula || '(sin título)'}</span>
        {cfg && (
          <span className={`badge ${cfg.badge}`}>{cfg.label}</span>
        )}
      </div>

      {h.tipo_riesgo && (
        <div className="finding-type">{h.tipo_riesgo}</div>
      )}

      {h.explicacion && (
        <p className="finding-explicacion">{h.explicacion}</p>
      )}

      {h.cita_textual && (
        <blockquote className="finding-cita">
          "{h.cita_textual.length > 180
            ? h.cita_textual.slice(0, 180) + '…'
            : h.cita_textual}"
        </blockquote>
      )}

      {h.requiere_revision_humana && (
        <div className="finding-revision-flag">
          <span>⚠ Requiere revisión humana</span>
          {h.motivo_revision && (
            <span className="finding-revision-motivo">
              {h.motivo_revision.length > 100
                ? h.motivo_revision.slice(0, 100) + '…'
                : h.motivo_revision}
            </span>
          )}
        </div>
      )}
    </button>
  )
}

// ── Panel derecho completo ───────────────────────────────────────────────────

export default function FindingsList({ resumen, hallazgos, selectedFinding, onSelectFinding }) {
  // Todos los conteos salen de los datos reales (no valores fijos)
  const { porNivel, sinRiesgo } = useMemo(() => {
    const porNivel  = { alto: [], medio: [], bajo: [] }
    const sinRiesgo = []

    for (const h of hallazgos) {
      if (h.riesgo_detectado && h.nivel_riesgo && porNivel[h.nivel_riesgo] !== undefined) {
        porNivel[h.nivel_riesgo].push(h)
      } else if (!h.riesgo_detectado) {
        sinRiesgo.push(h)
      }
    }
    return { porNivel, sinRiesgo }
  }, [hallazgos])

  const handleClick = (h) => {
    onSelectFinding(h)
  }

  return (
    <div className="findings-list">

      {/* ── Resumen — todos los números vienen del objeto resumen de la API ── */}
      <div className="findings-summary">
        <div className="summary-stat">
          <span className="summary-num">{resumen.total_clausulas}</span>
          <span className="summary-lbl">cláusulas</span>
        </div>
        <div className="summary-divider" />
        <div className="summary-stat">
          <span className="summary-num">{resumen.con_riesgo}</span>
          <span className="summary-lbl">con riesgo</span>
        </div>
        <div className="summary-divider" />
        <div className="summary-stat">
          <span className={`summary-num ${resumen.requieren_revision > 0 ? 'summary-num-warn' : ''}`}>
            {resumen.requieren_revision}
          </span>
          <span className="summary-lbl">para revisar</span>
        </div>
        <div className="summary-pills">
          {Object.entries(resumen.por_nivel).map(([nivel, count]) =>
            count > 0 ? (
              <span key={nivel} className={`summary-pill summary-pill-${nivel}`}>
                {count} {nivel}
              </span>
            ) : null
          )}
        </div>
      </div>

      {/* ── Hallazgos por nivel (alto → medio → bajo) ── */}
      {(['alto', 'medio', 'bajo']).map(nivel => {
        const grupo = porNivel[nivel]
        if (!grupo.length) return null
        const { icon, label } = NIVEL_CONFIG[nivel]
        return (
          <section key={nivel} className="findings-group">
            <h3 className="findings-group-title">
              {icon} RIESGO {label}{' '}
              <span className="findings-group-count">({grupo.length})</span>
            </h3>
            {grupo.map(h => (
              <FindingCard
                key={h.numero_clausula}
                h={h}
                isSelected={selectedFinding?.numero_clausula === h.numero_clausula}
                onClick={() => handleClick(h)}
              />
            ))}
          </section>
        )
      })}

      {/* ── Sin riesgo identificado ── */}
      {sinRiesgo.length > 0 && (
        <section className="findings-group">
          <h3 className="findings-group-title">
            ⚪ SIN RIESGO{' '}
            <span className="findings-group-count">({sinRiesgo.length})</span>
          </h3>
          <div className="findings-clean-list">
            {sinRiesgo.map(h => (
              <span key={h.numero_clausula} className="finding-clean-item">
                [{h.numero_clausula}] {h.titulo_clausula || '(sin título)'}
              </span>
            ))}
          </div>
        </section>
      )}

    </div>
  )
}
