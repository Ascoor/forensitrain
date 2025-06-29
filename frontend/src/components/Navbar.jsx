import React from 'react';
import { useTranslation } from 'react-i18next';

const Navbar = ({ toggleTheme, theme }) => {
  const { i18n, t } = useTranslation();
  const changeLang = (e) => {
    i18n.changeLanguage(e.target.value);
  };
  return (
    <div className="flex justify-between mb-4">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <div className="flex items-center gap-2">
        <select onChange={changeLang} className="border p-1 rounded">
          <option value="en">EN</option>
          <option value="ar">AR</option>
        </select>
        <button onClick={toggleTheme} className="border px-2 py-1 rounded">
          {theme === 'dark' ? '🌙' : '☀️'}
        </button>
      </div>
    </div>
  );
};

export default Navbar;
