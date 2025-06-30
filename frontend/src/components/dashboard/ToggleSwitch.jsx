import React from 'react';

/**
 * Styled toggle switch reminiscent of aircraft cockpit switches.
 */
const ToggleSwitch = ({ label, value, onChange }) => (
  <label className="flex items-center gap-2 cursor-pointer select-none">
    <span className="text-sm text-gray-300">{label}</span>
    <input
      type="checkbox"
      checked={value}
      onChange={(e) => onChange(e.target.checked)}
      className="sr-only"
    />
    <span
      className={`relative inline-block w-12 h-6 rounded-full transition-colors duration-300 ${value ? 'bg-green-500' : 'bg-gray-600'}`}
    >
      <span
        className={`absolute left-0 top-0 w-6 h-6 bg-gray-900 rounded-full transform transition-transform duration-300 ${value ? 'translate-x-6' : ''}`}
      />
    </span>
  </label>
);

export default ToggleSwitch;
