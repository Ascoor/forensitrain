import React, { useEffect, useState } from 'react';

const ACCENTS = {
  blue: 'text-blue-400',
  green: 'text-green-400',
  orange: 'text-orange-400',
};

const StatsCard = ({ label, value, accent = 'blue' }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let frame;
    const duration = 800;
    const start = performance.now();
    const animate = (time) => {
      const progress = Math.min((time - start) / duration, 1);
      setDisplay(Math.floor(progress * value));
      if (progress < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [value]);
  const color = ACCENTS[accent] || ACCENTS.blue;
  return (
    <div className="p-4 rounded-lg shadow bg-gray-800/60 backdrop-blur-lg">
      <p className="text-sm uppercase text-gray-400">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>{display}</p>
    </div>
  );
};

export default StatsCard;
