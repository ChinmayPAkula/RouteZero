// src/components/RouteLine.jsx
import { Polyline } from 'react-leaflet';

// Takes the ordered route array and draws a line connecting every
// location in sequence — exactly the order it was given, no reordering.
function RouteLine({ locations }) {
  const positions = locations.map((loc) => [loc.lat, loc.lng]);

  return (
    <Polyline
      positions={positions}
      pathOptions={{
        color: '#2563eb',
        weight: 3,
        opacity: 0.8,
        dashArray: '6, 6', // dashed = signals "straight-line estimate", not a real road path
      }}
    />
  );
}

export default RouteLine;