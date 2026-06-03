import { useState, useCallback, useRef } from 'react'

export default function UploadZone({ onUpload }) {
  const [dragOver, setDragOver]     = useState(false)
  const [selectedFile, setSelected] = useState(null)
  const inputRef = useRef(null)

  const handleFile = useCallback((file) => {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Solo se aceptan archivos PDF.')
      return
    }
    setSelected(file)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }, [handleFile])

  const handleDragOver  = useCallback((e) => { e.preventDefault(); setDragOver(true) }, [])
  const handleDragLeave = useCallback(() => setDragOver(false), [])
  const handleChange    = useCallback((e) => handleFile(e.target.files[0]), [handleFile])

  const handleSubmit = useCallback(() => {
    if (selectedFile) onUpload(selectedFile)
  }, [selectedFile, onUpload])

  const handleClear = useCallback((e) => {
    e.stopPropagation()
    setSelected(null)
    if (inputRef.current) inputRef.current.value = ''
  }, [])

  const handleZoneKey = useCallback((e) => {
    if (e.key === 'Enter' && !selectedFile) inputRef.current?.click()
  }, [selectedFile])

  return (
    <div className="upload-screen">
      <div className="upload-container">
        <h1 className="upload-title">Analizá tu contrato</h1>
        <p className="upload-desc">
          Subí un contrato con proveedores en PDF. El sistema detecta cláusulas de
          riesgo, las clasifica por severidad y cita el texto exacto donde aparecen.
        </p>

        <div
          className={`upload-zone ${dragOver ? 'drag-over' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !selectedFile && inputRef.current?.click()}
          onKeyDown={handleZoneKey}
          role="button"
          tabIndex={0}
          aria-label="Zona de carga de PDF"
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            onChange={handleChange}
            style={{ display: 'none' }}
            aria-hidden="true"
          />

          {selectedFile ? (
            <div className="upload-selected">
              <span className="upload-file-icon">📄</span>
              <span className="upload-file-name">{selectedFile.name}</span>
              <button
                className="upload-clear"
                onClick={handleClear}
                title="Quitar archivo"
                aria-label="Quitar archivo seleccionado"
              >×</button>
            </div>
          ) : (
            <>
              <span className="upload-dropicon" aria-hidden="true">⬆</span>
              <p className="upload-zone-text">
                Arrastrá un PDF aquí o hacé click para seleccionarlo
              </p>
              <p className="upload-zone-hint">
                Solo contratos con texto seleccionable (no documentos escaneados)
              </p>
            </>
          )}
        </div>

        <button
          className="btn-primary btn-large"
          disabled={!selectedFile}
          onClick={handleSubmit}
        >
          Analizar contrato
        </button>

        <p className="upload-disclaimer">
          ⚠&nbsp; Herramienta de asistencia. No reemplaza la revisión de un
          profesional del derecho.
        </p>
      </div>
    </div>
  )
}
