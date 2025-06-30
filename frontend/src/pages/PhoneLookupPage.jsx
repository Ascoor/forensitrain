import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import PhoneInput from '../components/PhoneInput' 
import GraphView from '../components/GraphView'
 

/**
 * PhoneLookupPage renders the phone search form and results.
 * It demonstrates real-time validation, loading indicator,
 * error handling and result tabs.
 */
const PhoneLookupPage = ({ onSearch, loading, error, result }) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState('general')
 
  const tabs = ['general', 'accounts', 'breaches', 'emails', 'graph']
 
  return (
    <div>
      <PhoneInput onSearch={onSearch} />
      {loading && (
        <div className="flex justify-center my-4">
          <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      {error && <p className="text-red-600 mb-2">{error}</p>}
      {result && (
        <div className="border p-4 rounded shadow">
          <div className="flex gap-2 mb-2">
            {tabs.map((key) => (
              <button
                key={key}
                className={`px-2 py-1 border rounded ${tab === key ? 'bg-blue-500 text-white' : ''}`}
                onClick={() => setTab(key)}
              >
                {t(key)}
              </button>
            ))}
          </div>

          {tab === 'general' && (
            <div>
              <p><strong>Phone:</strong> {result.phone_number}</p>
              <p><strong>Valid:</strong> {result.valid ? 'Yes' : 'No'}</p>
              <p><strong>Country:</strong> {result.country}</p>
              <p><strong>Carrier:</strong> {result.carrier || 'N/A'}</p>
              {result.line_type && (
                <p><strong>Line Type:</strong> {result.line_type}</p>
              )}
            </div>
          )}

          {tab === 'accounts' && (
            <div>
              {result.accounts && result.accounts.length > 0 ? (
                <ul className="list-disc list-inside">
                  {result.accounts.map((acc, i) => (
                    <li key={i}>
                      <a href={acc.url || acc} target="_blank" rel="noopener noreferrer" className="hover:underline">
                        {acc.username || acc}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No accounts found.</p>
              )}
            </div>
          )}

          {tab === 'breaches' && (
            <div>
              {result.breaches && result.breaches.length > 0 ? (
                <ul className="list-disc list-inside">
                  {result.breaches.map((b, i) => (
                    <li key={i}>{b}</li>
                  ))}
                </ul>
              ) : (
                <p>No breaches found.</p>
              )}
            </div>
          )}

          {tab === 'emails' && (
            <div>
              {result.emails && result.emails.length > 0 ? (
                <ul className="list-disc list-inside">
                  {result.emails.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              ) : (
                <p>No emails found.</p>
              )}
            </div>
          )} 

          {tab === 'graph' && (
            <div className="mt-2">
              <GraphView graph={result.graph} />
            </div>
          )}
 
        </div>
      )}
    </div>
  )
}

export default PhoneLookupPage
