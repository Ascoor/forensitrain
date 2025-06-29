import React, { useState } from 'react'
import { analyzeImage } from '../services/api'
import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'

const spinnerVariants = {
  animate: { rotate: 360 },
  transition: { repeat: Infinity, duration: 1, ease: 'linear' }
}

const ImageAnalysis = () => {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { t } = useTranslation()

  const handleFile = (e) => {
    setFile(e.target.files[0])
  }

  const submit = async () => {
    if (!file) return
    try {
      setLoading(true)
      setResult(null)
      setError(null)
      const data = await analyzeImage(file)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="border p-4 rounded mb-4 text-center">
        <input type="file" onChange={handleFile} className="mb-2" />
        <button onClick={submit} className="bg-blue-500 text-white px-4 py-2 rounded">
          {t('scan')}
        </button>
        {loading && (
          <motion.div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mt-4" animate="animate" variants={spinnerVariants} />
        )}
        {error && <p className="text-red-600 mt-2">{error}</p>}
      </div>
      {result && (
        <div className="space-y-2">
          <h2 className="text-xl font-semibold">{t('image_info')}</h2>
          <p><strong>Dimensions:</strong> {result.dimensions}</p>
          <p><strong>Format:</strong> {result.format}</p>
          {result.exif && <p><strong>EXIF:</strong> {Object.keys(result.exif).length} tags</p>}
          <h3 className="font-semibold">{t('detected_faces')}: {result.faces_detected}</h3>
          {result.text && (
            <div>
              <h3 className="font-semibold">{t('extracted_text')}</h3>
              <pre className="whitespace-pre-wrap bg-gray-100 p-2 rounded">{result.text}</pre>
            </div>
          )}
          {result.objects && result.objects.length > 0 && (
            <div>
              <h3 className="font-semibold">{t('scene_elements')}</h3>
              <ul className="list-disc list-inside">
                {result.objects.map((o, i) => <li key={i}>{o}</li>)}
              </ul>
            </div>
          )}
          {result.inferred_platform && (
            <p><strong>{t('inferred_clues')}:</strong> {result.inferred_platform}</p>
          )}
        </div>
      )}
    </div>
  )
}

export default ImageAnalysis
