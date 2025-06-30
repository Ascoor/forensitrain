import React, { useEffect, useState } from 'react';

const sample = [
  'New phone number +12024561111 collected',
  'Email test@example.com verified',
  'Image processed: IMG_001.png',
];

const DataStreamPanel = () => {
  const [items, setItems] = useState(sample);
  useEffect(() => {
    const id = setInterval(() => {
      setItems((prev) => [
        `Activity ${prev.length + 1} detected`,
        ...prev.slice(0, 49),
      ]);
    }, 5000);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 h-64 overflow-auto">
      <p className="mb-2 font-semibold">Live Stream</p>
      <ul className="space-y-1 text-sm">
        {items.map((i, idx) => (
          <li key={idx} className="animate-fade-in">{i}</li>
        ))}
      </ul>
    </div>
  );
};

export default DataStreamPanel;
