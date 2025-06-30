import React, { useState } from 'react';
import Sidebar from '../components/dashboard/Sidebar';
import ProfileMenu from '../components/dashboard/ProfileMenu';
import StatsCard from '../components/dashboard/StatsCard';
import StatsCharts from '../components/dashboard/StatsCharts';
import MapWidget from '../components/dashboard/MapWidget';
import DataStreamPanel from '../components/dashboard/DataStreamPanel';
import SocialAccountsPanel from '../components/dashboard/SocialAccountsPanel';
import ImageGrid from '../components/dashboard/ImageGrid';
import AlertCenter from '../components/dashboard/AlertCenter';
import AnalogGauge from '../components/dashboard/AnalogGauge';
import RadarScope from '../components/dashboard/RadarScope';
import ToggleSwitch from '../components/dashboard/ToggleSwitch';
import { motion } from 'framer-motion';

const stats = [
  { label: 'New Data', value: 1234, accent: 'blue' },
  { label: 'Verified Contacts', value: 567, accent: 'green' },
  { label: 'Active Alerts', value: 9, accent: 'orange' },
];

const DashboardPage = () => {
  const [systems, setSystems] = useState({ radar: true, gauges: true });
  return (
    <div className="flex h-full bg-gray-900 text-gray-100 font-sans flicker">
      <Sidebar />
      <main className="flex-1 overflow-auto p-4 space-y-4">
        <div className="flex justify-between items-center">
          <ProfileMenu />
          <div className="flex gap-4">
            <ToggleSwitch
              label="Radar"
              value={systems.radar}
              onChange={(v) => setSystems((s) => ({ ...s, radar: v }))}
            />
            <ToggleSwitch
              label="Gauges"
              value={systems.gauges}
              onChange={(v) => setSystems((s) => ({ ...s, gauges: v }))}
            />
          </div>
        </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((s, idx) => (
          <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}>
            <StatsCard label={s.label} value={s.value} accent={s.accent} />
          </motion.div>
        ))}
      </div>
      <StatsCharts />
      {systems.gauges && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AnalogGauge label="Signal" value={80} />
          <AnalogGauge label="Threat" value={30} />
          <AnalogGauge label="Load" value={65} />
          <AnalogGauge label="Integrity" value={95} />
        </div>
      )}
      {systems.radar && <RadarScope />}
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
};

export default DashboardPage;
