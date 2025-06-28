export const analyzePhone = async (phoneNumber) => {
  const res = await fetch('http://localhost:8000/api/phone/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phoneNumber })
  })
  if (!res.ok) {
    throw new Error('Request failed')
  }
  return res.json()
}
