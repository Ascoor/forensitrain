import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'

const PhoneInput = ({ onSearch }) => {
  const [phone, setPhone] = useState('')
  const { t } = useTranslation()

  const submit = (e) => {
    e.preventDefault()
    if (onSearch) {
      onSearch(phone)
    }
  }

  return (
    <form onSubmit={submit} className="flex gap-2 mb-4">
      <input
        type="text"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        placeholder={t('search_placeholder')}
        className="border p-2 flex-1"
      />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2">
        {t('search')}
      </button>
    </form>
  )
}

export default PhoneInput
