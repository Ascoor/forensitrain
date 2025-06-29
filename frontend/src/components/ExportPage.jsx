import React from 'react';
import { exportReport } from '../services/api';

const ExportPage = ({ phone }) => {
  const handleExport = async () => {
    const blob = await exportReport(phone, 'pdf');
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'report.pdf';
    a.click();
    window.URL.revokeObjectURL(url);
  };
  return (
    <button onClick={handleExport} className="bg-green-500 text-white px-4 py-2 rounded">
      Download PDF
    </button>
  );
};

export default ExportPage;
