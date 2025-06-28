import React from 'react'

const ResultCard = ({ data }) => {
  return (
    <div className="border p-4 rounded shadow">
      <p><strong>Phone:</strong> {data.phone_number}</p>
      <p><strong>Name:</strong> {data.name}</p>
      <p><strong>Country:</strong> {data.country}</p>
      <p><strong>Email:</strong> {data.email}</p>
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
    </div>
  )
}

export default ResultCard
