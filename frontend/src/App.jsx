import React, { useState } from 'react'
import PhoneInput from './components/PhoneInput'
import ResultCard from './components/ResultCard'
import { analyzePhone } from './services/api'

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async (phone) => {
    try {
      setLoading(true)
      const data = await analyzePhone(phone)
      setResult(data)
    } catch (err) {
      console.error(err)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">ForensiTrain</h1>
      <PhoneInput onSearch={handleSearch} />
      {loading && <p className="mb-2">Loading...</p>}
      {result && <ResultCard data={result} />}
      <p className="text-xs text-gray-600 mt-4">This tool is for lawful OSINT use only. The creators are not responsible for misuse.</p>
    </div>
  )
}

export default App
