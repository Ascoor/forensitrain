import React from 'react';
import Sidebar from '../components/dashboard/Sidebar';
import ProfileMenu from '../components/dashboard/ProfileMenu';
import StatsCard from '../components/dashboard/StatsCard';
import StatsCharts from '../components/dashboard/StatsCharts';
import MapWidget from '../components/dashboard/MapWidget';
import DataStreamPanel from '../components/dashboard/DataStreamPanel';
import SocialAccountsPanel from '../components/dashboard/SocialAccountsPanel';
import ImageGrid from '../components/dashboard/ImageGrid';
import AlertCenter from '../components/dashboard/AlertCenter';
import { motion } from 'framer-motion';

const stats = [
  { label: 'New Data', value: 1234, accent: 'blue' },
  { label: 'Verified Contacts', value: 567, accent: 'green' },
  { label: 'Active Alerts', value: 9, accent: 'orange' },
];

const DashboardPage = () => (
  <div className="flex h-full bg-gray-900 text-gray-100 font-sans">
    <Sidebar />
    <main className="flex-1 overflow-auto p-4 space-y-4">
      <div className="flex justify-end">
        <ProfileMenu />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((s, idx) => (
          <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}>
            <StatsCard label={s.label} value={s.value} accent={s.accent} />
          </motion.div>
        ))}
      </div>
      <StatsCharts />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <MapWidget />
        <AlertCenter />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DataStreamPanel />
        <SocialAccountsPanel />
        <ImageGrid />
      </div>
    </main>
  </div>
);

export default DashboardPage;
