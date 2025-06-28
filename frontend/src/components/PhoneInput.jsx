import React, { useState } from 'react'

const PhoneInput = ({ onSearch }) => {
  const [phone, setPhone] = useState('')

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
        placeholder="Enter phone number"
        className="border p-2 flex-1"
      />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2">
        Search
      </button>
    </form>
  )
}

export default PhoneInput
