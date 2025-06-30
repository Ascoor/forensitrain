import React from 'react';
import { LineChart, Line, BarChart, Bar, RadialBarChart, RadialBar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const lineData = [
  { name: 'Mon', queries: 30 },
  { name: 'Tue', queries: 45 },
  { name: 'Wed', queries: 50 },
  { name: 'Thu', queries: 65 },
  { name: 'Fri', queries: 40 },
  { name: 'Sat', queries: 55 },
  { name: 'Sun', queries: 30 },
];

const barData = [
  { name: 'Emails', count: 400 },
  { name: 'Phones', count: 300 },
  { name: 'Images', count: 200 },
  { name: 'Profiles', count: 278 },
];

const radialData = [
  { name: 'Verification', value: 76, fill: '#60a5fa' },
];

const StatsCharts = () => (
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <div className="bg-gray-800/60 backdrop-blur-lg p-4 rounded shadow h-64">
      <p className="mb-2 font-semibold">Weekly Queries</p>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={lineData}>
          <CartesianGrid stroke="#374151" />
          <XAxis dataKey="name" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip />
          <Line type="monotone" dataKey="queries" stroke="#60a5fa" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
    <div className="bg-gray-800/60 backdrop-blur-lg p-4 rounded shadow h-64">
      <p className="mb-2 font-semibold">Data Types</p>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={barData}>
          <CartesianGrid stroke="#374151" />
          <XAxis dataKey="name" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip />
          <Bar dataKey="count" fill="#34d399" />
        </BarChart>
      </ResponsiveContainer>
    </div>
    <div className="bg-gray-800/60 backdrop-blur-lg p-4 rounded shadow h-64 flex items-center justify-center">
      <ResponsiveContainer width="100%" height="80%">
        <RadialBarChart innerRadius="80%" outerRadius="100%" data={radialData} startAngle={180} endAngle={0}>
          <RadialBar minAngle={15} background clockWise dataKey="value" />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute text-2xl text-blue-400 font-bold">76%</div>
    </div>
  </div>
);

export default StatsCharts;
