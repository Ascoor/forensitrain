import React from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

const GeoSocialMap = ({ data }) => (
  <MapContainer center={[20, 0]} zoom={2} className="h-96 w-full rounded">
    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {data.locations.map((loc, i) => (
      <Marker key={i} position={[loc.lat, loc.lon]}>
        <Popup>
          <p className="font-semibold mb-1">{loc.created_at}</p>
          <p>{loc.text}</p>
        </Popup>
      </Marker>
    ))}
  </MapContainer>
)

export default GeoSocialMap
