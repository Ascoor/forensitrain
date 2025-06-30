export const API_BASE =
  import.meta.env.VITE_API_BASE || '/api'

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

export const enrichPhone = async (phoneNumber) => {
  const res = await fetch(`${API_BASE}/phone/enrich`, {
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

export const exportReport = async (phoneNumber, fmt = 'json') => {
  const res = await fetch(`${API_BASE}/phone/export?fmt=${fmt}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phoneNumber })
  })
  if (!res.ok) {
    throw new Error('Request failed')
  }
  if (fmt === 'pdf') {
    const blob = await res.blob()
    return blob
  }
  return await res.json()
}

export const analyzeImage = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}/analyze-image`, {
    method: 'POST',
    body: form
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
