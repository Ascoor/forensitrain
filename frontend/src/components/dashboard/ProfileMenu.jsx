import React, { useState, useRef, useEffect } from 'react';
import { FiUser, FiChevronDown } from 'react-icons/fi';

const ProfileMenu = () => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handle = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('click', handle);
    return () => document.removeEventListener('click', handle);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-gray-200 hover:text-blue-400 focus:outline-none"
        aria-haspopup="true"
        aria-expanded={open}
      >
        <FiUser />
        <FiChevronDown />
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-40 bg-gray-800/70 backdrop-blur-md rounded shadow-lg py-2 text-sm" role="menu">
          <a href="#" className="block px-3 py-1 hover:bg-gray-700" role="menuitem">Settings</a>
          <a href="#" className="block px-3 py-1 hover:bg-gray-700" role="menuitem">Logout</a>
        </div>
      )}
    </div>
  );
};

export default ProfileMenu;
