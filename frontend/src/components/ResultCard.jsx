import React, { useState } from 'react'
import { FaFacebook, FaTwitter, FaInstagram } from 'react-icons/fa'

const platformIcon = (url) => {
  if (url.includes('facebook')) return <FaFacebook className="inline mr-1" />
  if (url.includes('twitter')) return <FaTwitter className="inline mr-1" />
  if (url.includes('instagram')) return <FaInstagram className="inline mr-1" />
  return null
}

const ResultCard = ({ data }) => {
  const [tab, setTab] = useState('general')
  const tabs = ['general', 'accounts', 'breaches']

  return (
    <div className="border p-4 rounded shadow">
      <div className="flex gap-2 mb-2">
        {tabs.map((t) => (
          <button
            key={t}
            className={`px-2 py-1 border rounded ${tab === t ? 'bg-blue-500 text-white' : ''}`}
            onClick={() => setTab(t)}
          >
            {t === 'general' && 'General Info'}
            {t === 'accounts' && 'Social Accounts'}
            {t === 'breaches' && 'Breach History'}
          </button>
        ))}
      </div>

      {tab === 'general' && (
        <div>
          <p><strong>Phone:</strong> {data.phone_number}</p>
          <p><strong>Valid:</strong> {data.valid ? 'Yes' : 'No'}</p>
          <p><strong>Name:</strong> {data.name || 'N/A'}</p>
          <p><strong>Country:</strong> {data.country}</p>
          <p><strong>Carrier:</strong> {data.carrier}</p>
          {data.line_type && (
            <p><strong>Line Type:</strong> {data.line_type}</p>
          )}
        </div>
      )}

      {tab === 'accounts' && (
        <div>
          {data.accounts && data.accounts.length > 0 ? (
            <ul className="list-disc list-inside">
              {data.accounts.map((acc, i) => (
                <li key={i}>{platformIcon(acc)}{acc}</li>
              ))}
            </ul>
          ) : (
            <p>No accounts found.</p>
          )}
        </div>
      )}

      {tab === 'breaches' && (
        <div>
          {data.breaches && data.breaches.length > 0 ? (
            <ul className="list-disc list-inside">
              {data.breaches.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          ) : (
            <p>No breaches found.</p>
          )}
        </div>
      )}
    </div>
  )
}

export default ResultCard
