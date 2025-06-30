import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { motion } from 'framer-motion';
import 'leaflet/dist/leaflet.css';

const sampleStats = [
  { name: 'New Data', value: 1234 },
  { name: 'Verified Contacts', value: 567 },
  { name: 'Alerts', value: 9 },
];

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

const alerts = [
  { id: 1, message: 'Possible breach detected', level: 'high', time: '10:24' },
  { id: 2, message: 'New social profile linked', level: 'medium', time: '11:15' },
  { id: 3, message: 'Image analysis completed', level: 'low', time: '12:05' },
];

const DashboardPage = () => (
  <div className="flex h-full bg-gray-900 text-gray-100">
    <aside className="w-64 bg-gray-800 p-4 hidden md:block">
      <h2 className="text-xl font-bold mb-4 text-blue-400">IntelBoard</h2>
      <nav className="space-y-2">
        <a href="#" className="block hover:text-blue-400">Dashboard</a>
        <a href="#" className="block hover:text-blue-400">Phone Lookup</a>
        <a href="#" className="block hover:text-blue-400">Image Analysis</a>
      </nav>
    </aside>
    <main className="flex-1 overflow-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {sampleStats.map((s, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-gray-800 p-4 rounded shadow"
          >
            <p className="text-sm uppercase text-gray-400">{s.name}</p>
            <p className="text-2xl font-bold text-blue-400">{s.value}</p>
          </motion.div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-800 p-4 rounded shadow h-64">
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
        <div className="bg-gray-800 p-4 rounded shadow h-64">
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
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-800 p-4 rounded shadow h-64">
          <p className="mb-2 font-semibold">Activity Map</p>
          <MapContainer center={[51.505, -0.09]} zoom={2} className="h-full w-full">
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <Marker position={[51.505, -0.09]}>
              <Popup>Sample location</Popup>
            </Marker>
          </MapContainer>
        </div>
        <div className="bg-gray-800 p-4 rounded shadow overflow-auto">
          <p className="mb-2 font-semibold">Alerts</p>
          <ul className="space-y-2">
            {alerts.map(a => (
              <li key={a.id} className="border-b border-gray-700 pb-2">
                <span className={`mr-2 px-2 py-0.5 text-xs rounded ${a.level === 'high' ? 'bg-red-500' : a.level === 'medium' ? 'bg-yellow-500' : 'bg-green-500'}`}>{a.level.toUpperCase()}</span>
                {a.message}
                <span className="float-right text-xs text-gray-400">{a.time}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  </div>
);

export default DashboardPage;
