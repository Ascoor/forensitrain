import React from 'react';

/**
 * Analog style gauge with digital readout for displaying vital statistics.
 * Uses SVG arcs and rotation for the needle animation.
 */
const AnalogGauge = ({ value = 50, max = 100, label = 'Gauge' }) => {
  // Clamp the value between 0 and max
  const val = Math.max(0, Math.min(value, max));
  const angle = (val / max) * 180 - 90; // 180deg sweep
  return (
    <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 flex flex-col items-center">
      <svg viewBox="0 0 100 60" className="w-full h-32">
        <path
          d="M10 50 A40 40 0 0 1 90 50"
          fill="none"
          stroke="#1f2937"
          strokeWidth="6"
        />
        <path
          d="M10 50 A40 40 0 0 1 90 50"
          fill="none"
          stroke="#0ea5e9"
          strokeWidth="6"
          strokeDasharray="125"
          strokeDashoffset={125 - (val / max) * 125}
        />
        <line
          x1="50"
          y1="50"
          x2="50"
          y2="15"
          stroke="#f43f5e"
          strokeWidth="2"
          transform={`rotate(${angle} 50 50)`}
        />
      </svg>
      <div className="mt-2 text-center">
        <p className="text-sm uppercase text-gray-400">{label}</p>
        <p className="text-xl font-mono text-blue-400">{val}</p>
      </div>
    </div>
  );
};

export default AnalogGauge;
