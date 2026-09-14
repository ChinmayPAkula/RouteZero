import { Marker, Popup } from 'react-leaflet';
import { divIcon } from 'leaflet';
import { Warehouse, Package } from 'lucide-react';
import { renderToStaticMarkup } from 'react-dom/server';

// Builds a Leaflet divIcon from a Lucide icon + background color.
// We use renderToStaticMarkup because Leaflet needs a plain HTML string,
// not a live React element.
function createIcon(IconComponent, bgColor) {
  const html = renderToStaticMarkup(
    <div
      style={{
        background: bgColor,
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '2px solid white',
        boxShadow: '0 1px 4px rgba(0,0,0,0.4)',
      }}
    >
      <IconComponent color="white" size={18} />
    </div>
  );

  return divIcon({
    html,
    className: '', // prevents Leaflet's default marker CSS from leaking in
    iconSize: [32, 32],
    iconAnchor: [16, 16], // centers the icon exactly on the coordinate
  });
}

const depotIcon = createIcon(Warehouse, '#1e293b');   // dark slate
const deliveryIcon = createIcon(Package, '#059669');  // green

function LocationMarker({ location, stopNumber }) {
  const isDepot = location.type === 'depot';

  return (
    <Marker
      position={[location.lat, location.lng]}
      icon={isDepot ? depotIcon : deliveryIcon}
    >
      <Popup>
        <strong>{location.name}</strong>
        <br />
        {isDepot ? 'Depot' : `Stop #${stopNumber}`}
      </Popup>
    </Marker>
  );
}

export default LocationMarker;