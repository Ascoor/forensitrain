import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

const PhoneInput = ({ onSearch }) => {
  const [phone, setPhone] = useState('')
  const [isValid, setIsValid] = useState(false)
  const { t } = useTranslation()

  useEffect(() => {
    const pattern = /^\+?[1-9]\d{6,14}$/
    setIsValid(pattern.test(phone))
  }, [phone])

  const submit = (e) => {
    e.preventDefault()
    if (onSearch) {
      onSearch(phone)
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-2 mb-4">
      <input
        type="text"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        placeholder={t('search_placeholder')}
        className={`border p-2 flex-1 ${phone && !isValid ? 'border-red-500' : ''}`}
      />
      {!isValid && phone && (
        <span className="text-red-600 text-sm">{t('invalid_phone')}</span>
      )}
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 disabled:opacity-50"
        disabled={!isValid}
      >
        {t('search')}
      </button>
    </form>
  )
}

export default PhoneInput
