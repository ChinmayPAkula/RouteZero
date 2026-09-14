// src/components/MapView.jsx
import { useState, useEffect } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import LocationMarker from './LocationMarker';
import RouteLine from './RouteLine';
import RoutePanel from './RoutePanel';
import Header from './Header';
import Legend from './Legend';
import { fetchOptimizedRoute } from '../api/routeApi';

function MapView() {
  const defaultCenter = [12.9716, 77.5946];
  const defaultZoom = 12;

  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOptimizedRoute()
        .then((data) => {
    if (!data || !Array.isArray(data.route) || data.route.length === 0) {
        throw new Error('Empty or invalid route data');
    }

    // Filter out any location missing valid numeric coordinates,
    // so one bad record from the backend can't crash the whole map.
    const validLocations = data.route.filter(
        (loc) => typeof loc.lat === 'number' && typeof loc.lng === 'number'
    );

    if (validLocations.length === 0) {
        throw new Error('No valid coordinates in route data');
    }

    setLocations(validLocations);
    })
      .catch(() => {
        setError('Unable to load optimized route. Please try again.');
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif', color: '#64748b' }}>
        Loading route...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif', color: '#dc2626' }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100%' }}>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        <RouteLine locations={locations} />

        {locations.map((loc, index) => (
          <LocationMarker key={`${loc.id}-${index}`} location={loc} stopNumber={index} />
        ))}
      </MapContainer>

      <Header />
      <Legend />
      <RoutePanel locations={locations} />
    </div>
  );
}

export default MapView;