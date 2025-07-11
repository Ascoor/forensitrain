import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { FaFacebook, FaTwitter, FaInstagram } from 'react-icons/fa'

const platformIcon = (url) => {
  if (url.includes('facebook')) return <FaFacebook className="inline mr-1" />
  if (url.includes('twitter')) return <FaTwitter className="inline mr-1" />
  if (url.includes('instagram')) return <FaInstagram className="inline mr-1" />
  return null
}

const ResultCard = ({ data }) => {
  const [tab, setTab] = useState('general')
  const tabs = ['general', 'accounts', 'breaches', 'emails']
  const { t } = useTranslation()

  return (
    <div className="border p-4 rounded shadow">
      <div className="flex gap-2 mb-2">
       {tabs.map((tabKey) => (
  <button
    key={tabKey}
    className={`px-2 py-1 border rounded ${tab === tabKey ? 'bg-blue-500 text-white' : ''}`}
    onClick={() => setTab(tabKey)}
  >
    {tabKey === 'general' && t('general')}
    {tabKey === 'accounts' && t('accounts')}
    {tabKey === 'breaches' && t('breaches')}
    {tabKey === 'emails' && t('emails')}
  </button>
))}

      </div>

      {tab === 'general' && (
        <div>
          <p><strong>Phone:</strong> {data.phone_number}</p>
          <p>
            <strong>Valid:</strong>
            {data.valid ? (
              <span className="ml-1 px-2 py-0.5 text-xs bg-green-500 text-white rounded" title="Valid number">Yes</span>
            ) : (
              <span className="ml-1 px-2 py-0.5 text-xs bg-red-500 text-white rounded" title="Invalid number">No</span>
            )}
          </p>
          <p title="Location or owner name if available">
            <strong>Name:</strong> {data.name || 'N/A'}
          </p>
          <p><strong>Country:</strong> {data.country}</p>
          <p><strong>Carrier:</strong> {data.carrier || 'N/A'}</p>
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
                <li key={i}>
                  <a
                    href={acc}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                    title={acc}
                  >
                    {platformIcon(acc)}{acc}
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

      {tab === 'emails' && (
        <div>
          {data.emails && data.emails.length > 0 ? (
            <ul className="list-disc list-inside">
              {data.emails.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          ) : (
            <p>No emails found.</p>
          )}
          {data.email_breaches && data.email_breaches.length > 0 && (
            <div className="mt-2">
              <p className="font-semibold">Email Breaches:</p>
              <ul className="list-disc list-inside">
                {data.email_breaches.map((b, i) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ResultCard
