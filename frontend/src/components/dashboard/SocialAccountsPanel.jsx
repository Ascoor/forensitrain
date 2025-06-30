import React from 'react';
import { FiCheckCircle, FiClock } from 'react-icons/fi';

const accounts = [
  { platform: 'Twitter', user: '@intel', status: 'verified' },
  { platform: 'Facebook', user: 'John Doe', status: 'pending' },
  { platform: 'Instagram', user: '@instaUser', status: 'verified' },
];

const SocialAccountsPanel = () => (
  <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 h-64 overflow-auto">
    <p className="mb-2 font-semibold">Linked Accounts</p>
    <ul className="space-y-2 text-sm">
      {accounts.map((acc, idx) => (
        <li key={idx} className="flex items-center justify-between">
          <span>{acc.platform} - {acc.user}</span>
          {acc.status === 'verified' ? (
            <FiCheckCircle className="text-green-400" />
          ) : (
            <FiClock className="text-yellow-400" />
          )}
        </li>
      ))}
    </ul>
  </div>
);

export default SocialAccountsPanel;
