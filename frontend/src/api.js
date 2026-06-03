const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Envía un PDF a POST /analizar y devuelve el JSON de la respuesta.
 * Lanza un Error con el mensaje del servidor si el status no es 2xx.
 */
export async function analizarContrato(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/analizar`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    let detail = `Error ${res.status} al analizar el contrato`
    try {
      const err = await res.json()
      detail = err.detail || detail
    } catch {
      // si el body no es JSON, usar el mensaje genérico
    }
    throw new Error(detail)
  }

  return res.json()
}
