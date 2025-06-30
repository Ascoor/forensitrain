import React from 'react';

/**
 * Simple radar scope with sweeping animation using CSS.
 */
const RadarScope = () => (
  <div className="relative bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 h-64 flex items-center justify-center">
    <div className="radar w-48 h-48 rounded-full border-2 border-green-400 relative overflow-hidden">
      <div className="radar-sweep absolute inset-0" />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-1 h-1 bg-green-400 rounded-full" />
      </div>
    </div>
  </div>
);

export default RadarScope;
