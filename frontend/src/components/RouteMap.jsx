import { useEffect } from 'react'
import { ExternalLink, MapPin } from 'lucide-react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-routing-machine'
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css'

export default function RouteMap() {
  const pickup = [12.9716, 77.5946]
  const destination = [12.9352, 77.6245]

  useEffect(() => {
    const map = L.map('route-map').setView(pickup, 12)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map)

    L.Routing.control({
      waypoints: [
        L.latLng(...pickup),
        L.latLng(...destination),
      ],
      routeWhileDragging: false,
      addWaypoints: false,
      draggableWaypoints: false,
      show: false,
      lineOptions: {
        styles: [
          {
            color: '#16a34a',
            weight: 6,
            opacity: 0.8,
          },
        ],
      },
    }).addTo(map)

    return () => {
      map.remove()
    }
  }, [])

  const openGoogleMaps = () => {
    const url = `https://www.google.com/maps/dir/?api=1&origin=${pickup[0]},${pickup[1]}&destination=${destination[0]},${destination[1]}`
    window.open(url, '_blank')
  }

  return (
    <div className="bg-white rounded-2xl border border-ink-200 p-4 shadow-lg shadow-ink-900/5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-ink-900">
            Route Map
          </h2>
          <p className="text-sm text-ink-400">
            View your route and get directions
          </p>
        </div>

        <button
          onClick={openGoogleMaps}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-ink-900 text-white text-sm font-medium hover:bg-ink-700 transition-all shadow-sm hover:-translate-y-0.5"
        >
          <MapPin size={16} />
          Get Directions
          <ExternalLink size={14} />
        </button>
      </div>

      <div
        id="route-map"
        className="w-full h-[420px] rounded-xl overflow-hidden"
      />
    </div>
  )
}