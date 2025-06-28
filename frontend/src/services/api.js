export const API_BASE =
  import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export const analyzePhone = async (phoneNumber) => {
  const res = await fetch(`${API_BASE}/phone/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phoneNumber })
  })
  if (!res.ok) {
    throw new Error('Request failed')
  }
  const data = await res.json()
  if (data.status !== 'success') {
    throw new Error(data.errors || 'Request failed')
  }
  return data.data
}
