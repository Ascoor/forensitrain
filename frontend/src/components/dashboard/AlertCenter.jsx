import React, { useState } from 'react';
import { FiXCircle, FiAlertTriangle } from 'react-icons/fi';

const initialAlerts = [
  { id: 1, message: 'Possible breach detected', level: 'high', time: '10:24' },
  { id: 2, message: 'New social profile linked', level: 'medium', time: '11:15' },
  { id: 3, message: 'Image analysis completed', level: 'low', time: '12:05' },
];

const colors = {
  high: 'bg-red-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
};

const AlertCenter = () => {
  const [alerts, setAlerts] = useState(initialAlerts);
  const dismiss = (id) => setAlerts((a) => a.filter((al) => al.id !== id));
  return (
    <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 overflow-auto">
      <p className="mb-2 font-semibold">Alerts</p>
      <ul className="space-y-2">
        {alerts.map((a) => (
          <li key={a.id} className="flex items-center justify-between border-b border-gray-700 pb-1">
            <span className={`mr-2 px-2 py-0.5 text-xs rounded ${colors[a.level]}`}>{a.level.toUpperCase()}</span>
            <span className="flex-1 text-sm">{a.message}</span>
            <span className="text-xs text-gray-400 mr-2">{a.time}</span>
            <button onClick={() => dismiss(a.id)} aria-label="Dismiss">
              <FiXCircle className="text-gray-500 hover:text-red-400" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AlertCenter;
