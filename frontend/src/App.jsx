import React, { useState } from 'react'
import PhoneInput from './components/PhoneInput'
import ResultCard from './components/ResultCard'
import { analyzePhone } from './services/api'

function App() {
  const [result, setResult] = useState(null)

  const handleSearch = async (phone) => {
    try {
      const data = await analyzePhone(phone)
      setResult(data)
    } catch (err) {
      console.error(err)
      setResult(null)
    }
  }

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">ForensiTrain</h1>
      <PhoneInput onSearch={handleSearch} />
      {result && <ResultCard data={result} />}
    </div>
  )
}

export default App
