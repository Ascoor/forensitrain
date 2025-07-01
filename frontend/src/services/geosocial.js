import { API_BASE } from './api'

export const fetchFootprint = async (username) => {
  const res = await fetch(`${API_BASE}/geosocial/footprint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
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
