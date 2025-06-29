import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './i18n';
import Navbar from './components/Navbar';
import PhoneInput from './components/PhoneInput';
import ResultCard from './components/ResultCard';
import GraphView from './components/GraphView';
import ExportPage from './components/ExportPage';
import ImageAnalysis from './components/ImageAnalysis';
import { analyzePhone } from './services/api';

function LookupPage({ onSearch, loading, error, result }) {
  const { t } = useTranslation();
  return (
    <div>
      <PhoneInput onSearch={onSearch} />
      {loading && <p className="mb-2">{t('loading')}</p>}
      {error && <p className="text-red-600 mb-2">{error}</p>}
      {result && <ResultCard data={result} />}
    </div>
  );
}

function GraphPage({ result }) {
  if (!result) return null;
  return <GraphView graph={result.graph} />;
}

function App() {
  const { t } = useTranslation();
  const [theme, setTheme] = useState('light');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const toggleTheme = () => {
    setTheme((p) => (p === 'light' ? 'dark' : 'light'));
  };

  const handleSearch = async (phone) => {
    try {
      setError(null);
      setResult(null);
      setLoading(true);
      const data = await analyzePhone(phone);
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <BrowserRouter>
      <div className={theme === 'dark' ? 'dark' : ''}>
        <div className="p-4 max-w-3xl mx-auto text-gray-900 dark:bg-gray-800 dark:text-gray-100 min-h-screen">
          <Navbar toggleTheme={toggleTheme} theme={theme} />
          <nav className="mb-4 flex gap-4">
            <Link to="/">{t('general')}</Link>
            <Link to="/graph">Graph</Link>
            <Link to="/image">{t('image_analysis')}</Link>
            {result && <Link to="/export">{t('export')}</Link>}
          </nav>
          <Routes>
            <Route path="/" element={<LookupPage onSearch={handleSearch} loading={loading} error={error} result={result} />} />
            <Route path="/graph" element={<GraphPage result={result} />} />
            <Route path="/image" element={<ImageAnalysis />} />
            <Route path="/export" element={<ExportPage phone={result?.phone_number} />} />
          </Routes>
          <p className="text-xs mt-4">{t('legal')}</p>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
