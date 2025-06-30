import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const MapWidget = () => (
  <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 h-64">
    <p className="mb-2 font-semibold">Geo Activity</p>
    <MapContainer center={[20, 0]} zoom={2} className="h-full w-full rounded">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={[51.5, -0.09]}>
        <Popup>Sample location</Popup>
      </Marker>
    </MapContainer>
  </div>
);

export default MapWidget;
