import React, { useState, useEffect } from 'react'
import { analyzeImage } from '../services/api'
import { motion, AnimatePresence } from 'framer-motion'
import { useTranslation } from 'react-i18next'

// Simple spinner animation for the loading state
const spinnerVariants = {
  animate: { rotate: 360 },
  transition: { repeat: Infinity, duration: 1, ease: 'linear' }
}

// Only allow small JPEG or PNG files
const MAX_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED = ['image/jpeg', 'image/png']

const ImageAnalysis = () => {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { t } = useTranslation()

  // Validate and preview the selected file
  const handleFile = (e) => {
    const f = e.target.files[0]
    setResult(null)
    if (!f) return
    if (!ALLOWED.includes(f.type)) {
      setError(t('invalid_image'))
      setFile(null)
      setPreview(null)
      return
    }
    if (f.size > MAX_SIZE) {
      setError(t('file_too_large'))
      setFile(null)
      setPreview(null)
      return
    }
    setError(null)
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  // Clean up preview URL when component unmounts or file changes
  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [preview])

  // Send the file to the backend for analysis
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
        <label className="block mb-2">
          <span className="sr-only">{t('upload_image')}</span>
          <input
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFile}
            className="mx-auto"
          />
        </label>

        <AnimatePresence>
          {preview && (
            <motion.img
              key="preview"
              src={preview}
              alt="preview"
              className="mx-auto max-h-60 rounded mb-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
          )}
        </AnimatePresence>

        <button
          onClick={submit}
          disabled={!file || loading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {t('scan')}
        </button>

        {loading && (
          <motion.div
            className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mt-4"
            animate="animate"
            variants={spinnerVariants}
          />
        )}
        {error && <p className="text-red-600 mt-2">{error}</p>}
      </div>
      {/* Analysis results */}
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
