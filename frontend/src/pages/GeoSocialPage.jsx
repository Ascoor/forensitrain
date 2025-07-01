import React, { useState } from 'react'
import GeoSocialMap from '../components/GeoSocialMap'
import GeoSocialGlobe from '../components/GeoSocialGlobe'
import { fetchFootprint } from '../services/geosocial'

const GeoSocialPage = () => {
  const [username, setUsername] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchFootprint(username)
      setResult(data)
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4">
      <div className="flex gap-2 mb-4">
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Twitter handle"
          className="border p-2 rounded flex-grow"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {result && (
        <div className="grid md:grid-cols-2 gap-4">
          <GeoSocialMap data={result} />
          <GeoSocialGlobe data={result} />
        </div>
      )}
    </div>
  )
}

export default GeoSocialPage
