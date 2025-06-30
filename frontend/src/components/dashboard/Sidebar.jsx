import React, { useState } from 'react';
import { FiMenu, FiGrid, FiSearch, FiImage, FiAlertCircle } from 'react-icons/fi';

const Sidebar = () => {
  const [open, setOpen] = useState(true);
  const items = [
    { label: 'Dashboard', icon: <FiGrid /> },
    { label: 'Phone Lookup', icon: <FiSearch /> },
    { label: 'Image Analysis', icon: <FiImage /> },
    { label: 'Alerts', icon: <FiAlertCircle /> },
  ];
  return (
    <div className={`bg-gray-800/60 backdrop-blur-md text-gray-100 h-full p-4 transition-all duration-300 ${open ? 'w-64' : 'w-16'}`}> 
      <button
        className="text-gray-400 hover:text-blue-400 mb-6 focus:outline-none"
        onClick={() => setOpen(!open)}
        aria-label="Toggle sidebar"
      >
        <FiMenu />
      </button>
      <nav className="space-y-4">
        {items.map((item) => (
          <a
            key={item.label}
            href="#"
            className="flex items-center gap-2 hover:text-blue-400"
          >
            {item.icon}
            {open && <span>{item.label}</span>}
          </a>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
