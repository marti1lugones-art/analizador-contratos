import React, { useState, useCallback } from 'react'
import { analizarContrato } from './api'
import UploadZone from './components/UploadZone'
import ContractViewer from './components/ContractViewer'
import FindingsList from './components/FindingsList'

export default function App() {
  const [phase, setPhase]                   = useState('idle')   // idle | analyzing | done | error
  const [result, setResult]                 = useState(null)
  const [fileName, setFileName]             = useState('')
  const [selectedFinding, setSelectedFinding] = useState(null)
  const [errorMsg, setErrorMsg]             = useState('')

  const handleUpload = useCallback(async (file) => {
    setFileName(file.name)
    setPhase('analyzing')
    setSelectedFinding(null)
    setResult(null)
    setErrorMsg('')
    try {
      const data = await analizarContrato(file)
      setResult(data)
      setPhase('done')
    } catch (err) {
      setErrorMsg(err.message)
      setPhase('error')
    }
  }, [])

  const handleReset = useCallback(() => {
    setPhase('idle')
    setResult(null)
    setSelectedFinding(null)
    setErrorMsg('')
    setFileName('')
  }, [])

  const handleSelectFinding = useCallback((h) => {
    // Toggle: click en el mismo hallazgo lo deselecciona
    setSelectedFinding(prev =>
      prev?.numero_clausula === h.numero_clausula ? null : h
    )
  }, [])

  return (
    <div className="app">

      {/* ── Header ── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <span className="header-icon">⚖</span>
            <div>
              <span className="header-title">Analizador de Contratos</span>
              <span className="header-subtitle">Revisión de riesgo · contratos con proveedores · Argentina</span>
            </div>
          </div>
          {phase === 'done' && (
            <div className="header-right">
              <span className="header-filename" title={fileName}>{fileName}</span>
              <button className="btn-secondary" onClick={handleReset}>
                Nuevo contrato
              </button>
            </div>
          )}
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="app-main">

        {phase === 'idle' && (
          <UploadZone onUpload={handleUpload} />
        )}

        {phase === 'analyzing' && (
          <div className="analyzing-screen">
            <div className="analyzing-spinner" aria-hidden="true" />
            <p className="analyzing-text">Analizando contrato…</p>
            <p className="analyzing-sub">
              Claude está revisando las cláusulas. Puede tardar unos segundos.
            </p>
          </div>
        )}

        {phase === 'error' && (
          <div className="error-screen">
            <div className="error-icon">⚠</div>
            <h2 className="error-title">No se pudo analizar el contrato</h2>
            <p className="error-detail">{errorMsg}</p>
            <button className="btn-primary" onClick={handleReset}>
              Intentar de nuevo
            </button>
          </div>
        )}

        {phase === 'done' && result && (
          <div className="analysis-layout">

            <div className="panel panel-left">
              <div className="panel-header">
                <span className="panel-label">Texto del contrato</span>
                <span className="panel-hint">
                  {result.advertencia_segmentacion
                    ? '⚠ Sin estructura detectada'
                    : 'Hacé click en un hallazgo para resaltarlo'}
                </span>
              </div>
              <ContractViewer
                text={result.texto_completo}
                hallazgos={result.hallazgos}
                selectedFinding={selectedFinding}
              />
            </div>

            <div className="panel panel-right">
              <div className="panel-header">
                <span className="panel-label">Hallazgos</span>
              </div>
              <FindingsList
                resumen={result.resumen}
                hallazgos={result.hallazgos}
                selectedFinding={selectedFinding}
                onSelectFinding={handleSelectFinding}
              />
            </div>

          </div>
        )}

      </main>

      {/* ── Disclaimer — visible siempre que hay análisis activo ── */}
      {(phase === 'done' || phase === 'analyzing') && (
        <footer className="app-disclaimer">
          <span className="disclaimer-icon">⚠</span>
          <span>
            <strong>Herramienta de asistencia.</strong>{' '}
            No reemplaza la revisión de un profesional del derecho.
            Los hallazgos son orientativos y pueden requerir validación manual.
          </span>
        </footer>
      )}

    </div>
  )
}
