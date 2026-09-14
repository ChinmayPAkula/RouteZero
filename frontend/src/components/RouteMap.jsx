import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Map, Navigation, ExternalLink } from 'lucide-react'

export default function RouteMap({
  pickup,
  stops = [],
  destination,
  routeData,
}) {

  const mapContainerRef = useRef(null)
  const mapRef = useRef(null)
  const routeLayerRef = useRef(null)
  const markerLayerRef = useRef(null)

  const [routeReady, setRouteReady] = useState(false)
  const [error, setError] = useState('')
  const [distance, setDistance] = useState(null)
  const [duration, setDuration] = useState(null)

  useEffect(() => {

    if (!mapContainerRef.current || mapRef.current) {
      return
    }

    const map = L.map(mapContainerRef.current, {
      zoomControl: true,
      attributionControl: true,
    }).setView([20.5937, 78.9629], 5)

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }
    ).addTo(map)

    markerLayerRef.current =
      L.layerGroup().addTo(map)

    mapRef.current = map

    setTimeout(() => {
      map.invalidateSize()
    }, 300)

    return () => {
      map.remove()
      mapRef.current = null
      routeLayerRef.current = null
      markerLayerRef.current = null
    }

  }, [])


  useEffect(() => {

    if (!mapRef.current || !routeData) {
      return
    }

    if (
      !routeData.coordinates ||
      routeData.coordinates.length < 2
    ) {
      setError('No route coordinates were returned by the backend.')
      setRouteReady(false)
      return
    }

    setError('')

    if (routeLayerRef.current) {
      mapRef.current.removeLayer(
        routeLayerRef.current
      )

      routeLayerRef.current = null
    }

    if (markerLayerRef.current) {
      markerLayerRef.current.clearLayers()
    }

    const coordinates =
      routeData.coordinates
        .filter(
          (point) =>
            point &&
            Number.isFinite(Number(point.latitude)) &&
            Number.isFinite(Number(point.longitude))
        )
        .map((point) => ({
          name: point.name || '',
          latitude: Number(point.latitude),
          longitude: Number(point.longitude),
        }))


    if (coordinates.length < 2) {
      setError(
        'The backend returned invalid route coordinates.'
      )

      setRouteReady(false)
      return
    }


    const pickupIcon = L.divIcon({
      className: '',
      html: `
        <div style="
          width:18px;
          height:18px;
          background:#111827;
          border:3px solid white;
          border-radius:50%;
          box-shadow:0 2px 8px rgba(0,0,0,.3);
        "></div>
      `,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    })


    const stopIcon = L.divIcon({
      className: '',
      html: `
        <div style="
          width:18px;
          height:18px;
          background:#f59e0b;
          border:3px solid white;
          border-radius:50%;
          box-shadow:0 2px 8px rgba(0,0,0,.3);
        "></div>
      `,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    })


    const destinationIcon = L.divIcon({
      className: '',
      html: `
        <div style="
          width:18px;
          height:18px;
          background:#16a34a;
          border:3px solid white;
          border-radius:50%;
          box-shadow:0 2px 8px rgba(0,0,0,.3);
        "></div>
      `,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    })


    coordinates.forEach((point, index) => {

      let icon = stopIcon
      let label = `Stop ${index}`

      if (index === 0) {
        icon = pickupIcon
        label = 'Pickup'
      }

      if (index === coordinates.length - 1) {
        icon = destinationIcon
        label = 'Destination'
      }

      L.marker(
        [
          point.latitude,
          point.longitude,
        ],
        {
          icon,
        }
      )
        .bindPopup(
          `<b>${label}</b><br>${point.name || ''}`
        )
        .addTo(markerLayerRef.current)

    })


    const lineCoordinates =
      coordinates.map((point) => [
        point.latitude,
        point.longitude,
      ])


    routeLayerRef.current =
      L.polyline(
        lineCoordinates,
        {
          color: '#16a34a',
          weight: 6,
          opacity: 0.9,
        }
      ).addTo(mapRef.current)


    const bounds =
      routeLayerRef.current.getBounds()

    if (bounds.isValid()) {

      mapRef.current.fitBounds(
        bounds,
        {
          padding: [50, 50],
        }
      )

    }


    const backendDistance =
      Number(routeData.total_distance_km)

    const backendDuration =
      Number(routeData.total_duration_minutes)


    setDistance(
      Number.isFinite(backendDistance)
        ? backendDistance.toFixed(1)
        : null
    )

    setDuration(
      Number.isFinite(backendDuration)
        ? Math.round(backendDuration)
        : null
    )

    setRouteReady(true)

    setTimeout(() => {
      mapRef.current?.invalidateSize()
    }, 200)

  }, [routeData])


  const openGoogleMaps = () => {

    if (!pickup || !destination) {
      return
    }

    let googleMapsUrl =
      `https://www.google.com/maps/dir/?api=1` +
      `&origin=${encodeURIComponent(pickup)}` +
      `&destination=${encodeURIComponent(destination)}` +
      `&travelmode=driving`

    const validStops =
      stops.filter(
        (stop) => stop && stop.trim()
      )

    if (validStops.length > 0) {

      googleMapsUrl +=
        `&waypoints=${encodeURIComponent(
          validStops.join('|')
        )}`

    }

    window.open(
      googleMapsUrl,
      '_blank',
      'noopener,noreferrer'
    )
  }


  return (

    <div className="bg-white rounded-3xl border border-ink-200 shadow-lg shadow-ink-900/5 overflow-hidden">

      <div className="px-6 py-5 flex items-center justify-between border-b border-ink-100">

        <div className="flex items-center gap-4">

          <div className="w-12 h-12 rounded-xl bg-ink-900 flex items-center justify-center">

            <Map
              size={22}
              className="text-brand-400"
            />

          </div>

          <div>

            <p className="text-xs font-semibold tracking-[0.2em] text-brand-600 uppercase">
              Route Visualization
            </p>

            <h3 className="text-lg font-semibold text-ink-900">
              Optimized delivery path
            </h3>

          </div>

        </div>


        <div className="flex items-center gap-5">

          <div className="hidden sm:flex items-center gap-5 text-sm text-ink-600">

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-ink-900" />
              Pickup
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
              Stops
            </span>

            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-brand-500" />
              Destination
            </span>

          </div>


          <button
            onClick={openGoogleMaps}
            disabled={!pickup || !destination}
            className="hidden sm:flex items-center gap-2 bg-ink-900 hover:bg-ink-800 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl font-semibold transition"
          >

            <Navigation size={17} />

            Get Directions

            <ExternalLink size={15} />

          </button>

        </div>

      </div>


      <div className="relative">

        <div
          ref={mapContainerRef}
          className="w-full h-[430px]"
        />


        <div className="absolute top-5 left-5 z-[500] bg-white rounded-full px-5 py-3 shadow-lg flex items-center gap-2">

          <span
            className={`w-3 h-3 rounded-full ${
              error
                ? 'bg-red-500'
                : routeReady
                ? 'bg-green-500'
                : 'bg-gray-400'
            }`}
          />

          <span className="text-sm font-semibold text-ink-700">

            {error
              ? 'ROUTE ERROR'
              : routeReady
              ? 'ROUTE READY'
              : 'WAITING FOR ROUTE'}

          </span>

        </div>


        <div className="absolute bottom-5 left-5 z-[500] bg-white rounded-2xl px-5 py-4 shadow-xl">

          <p className="text-xs font-semibold tracking-wider text-ink-400 uppercase">
            Route Preview
          </p>

          <p className="text-base font-semibold text-ink-900 mt-1">

            {error
              ? 'Route unavailable'
              : routeReady
              ? 'Ready to navigate'
              : 'Waiting for backend route'}

          </p>

        </div>


        {routeReady && (

          <div className="absolute bottom-5 right-5 z-[500] bg-white border border-brand-200 rounded-full px-5 py-3 shadow-lg">

            <span className="text-sm font-semibold text-brand-600">
              RouteZero route
            </span>

          </div>

        )}


        {error && (

          <div className="absolute inset-0 z-[400] flex items-center justify-center pointer-events-none">

            <div className="bg-white/95 rounded-2xl shadow-xl px-6 py-5 max-w-md text-center">

              <p className="text-sm font-semibold text-red-600 mb-1">
                ROUTE ERROR
              </p>

              <p className="text-sm text-ink-600">
                {error}
              </p>

            </div>

          </div>

        )}

      </div>


      <div className="grid grid-cols-3 border-t border-ink-100">

        <div className="px-5 py-4">

          <p className="text-xs font-semibold text-ink-400 uppercase">
            Distance
          </p>

          <p className="text-base font-semibold text-ink-900 mt-1">
            {distance
              ? `${distance} km`
              : '--'}
          </p>

        </div>


        <div className="px-5 py-4 border-l border-ink-100">

          <p className="text-xs font-semibold text-ink-400 uppercase">
            Time
          </p>

          <p className="text-base font-semibold text-ink-900 mt-1">
            {duration
              ? `${duration} min`
              : '--'}
          </p>

        </div>


        <div className="px-5 py-4 border-l border-ink-100">

          <p className="text-xs font-semibold text-ink-400 uppercase">
            Navigation
          </p>

          <button
            onClick={openGoogleMaps}
            disabled={!pickup || !destination}
            className="text-base font-semibold text-brand-600 mt-1 hover:underline disabled:opacity-50"
          >
            Open Google Maps →
          </button>

        </div>

      </div>

    </div>
  )
}