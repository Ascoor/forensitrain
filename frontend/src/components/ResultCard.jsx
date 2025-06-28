import React from 'react'

const ResultCard = ({ data }) => {
  return (
    <div className="border p-4 rounded shadow">
      <p><strong>Phone:</strong> {data.phone_number}</p>
      <p><strong>Valid:</strong> {data.valid ? 'Yes' : 'No'}</p>
      <p><strong>Name:</strong> {data.name || 'N/A'}</p>
      <p><strong>Country:</strong> {data.country}</p>
      <p><strong>Carrier:</strong> {data.carrier}</p>
      {data.line_type && (
        <p><strong>Line Type:</strong> {data.line_type}</p>
      )}
      {data.accounts && (
        <div>
          <strong>Accounts:</strong>
          <ul className="list-disc list-inside">
            {data.accounts.map((acc, i) => (
              <li key={i}>{acc}</li>
            ))}
          </ul>
        </div>
      )}
      {data.breaches && data.breaches.length > 0 && (
        <div>
          <strong>Breaches:</strong>
          <ul className="list-disc list-inside">
            {data.breaches.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default ResultCard
