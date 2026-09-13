import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Map, Navigation, ExternalLink } from 'lucide-react'

export default function RouteMap({ pickup, destination }) {
  const mapContainerRef = useRef(null)
  const mapRef = useRef(null)

  const routeLayerRef = useRef(null)
  const markerLayerRef = useRef(null)

  // Prevent an older request from drawing over a newer route
  const requestIdRef = useRef(0)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [routeReady, setRouteReady] = useState(false)
  const [distance, setDistance] = useState(null)
  const [duration, setDuration] = useState(null)

  // --------------------------------------------------
  // CREATE MAP
  // --------------------------------------------------

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return

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

    markerLayerRef.current = L.layerGroup().addTo(map)

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

  // --------------------------------------------------
  // LOAD NEW ROUTE WHEN LOCATIONS CHANGE
  // --------------------------------------------------

  useEffect(() => {
    if (!pickup || !destination) {
      clearMap()

      setRouteReady(false)
      setError('')
      setDistance(null)
      setDuration(null)

      return
    }

    loadRoute()
  }, [pickup, destination])

  // --------------------------------------------------
  // CLEAR EVERYTHING FROM PREVIOUS ROUTE
  // --------------------------------------------------

  const clearMap = () => {
    if (!mapRef.current) return

    // Remove previous route line completely
    if (routeLayerRef.current) {
      mapRef.current.removeLayer(routeLayerRef.current)
      routeLayerRef.current = null
    }

    // Remove previous pickup/destination markers completely
    if (markerLayerRef.current) {
      markerLayerRef.current.clearLayers()
    }
  }

  // --------------------------------------------------
  // FIND LOCATION
  // --------------------------------------------------

  const searchLocation = async (location) => {
    const query = location.trim()

    if (!query) {
      throw new Error('Please enter a location.')
    }

    const url =
      `https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&limit=1`

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error('Unable to find this location.')
    }

    const data = await response.json()

    if (
      !data.features ||
      data.features.length === 0 ||
      !data.features[0].geometry
    ) {
      throw new Error(`Could not find "${location}".`)
    }

    const coordinates = data.features[0].geometry.coordinates

    return {
      longitude: Number(coordinates[0]),
      latitude: Number(coordinates[1]),
    }
  }

  // --------------------------------------------------
  // LOAD ROUTE
  // --------------------------------------------------

  const loadRoute = async () => {
    if (!mapRef.current) return

    // Give THIS request a unique ID
    const currentRequestId = ++requestIdRef.current

    setLoading(true)
    setError('')
    setRouteReady(false)
    setDistance(null)
    setDuration(null)

    // VERY IMPORTANT:
    // Remove the previous route before starting a new one
    clearMap()

    try {
      // Find pickup
      const start = await searchLocation(pickup)

      // If another search started while this was loading,
      // stop this old request completely
      if (currentRequestId !== requestIdRef.current) return

      await new Promise((resolve) => setTimeout(resolve, 200))

      // Find destination
      const end = await searchLocation(destination)

      // Check again before drawing anything
      if (currentRequestId !== requestIdRef.current) return

      // --------------------------------------------------
      // OSRM ROUTE
      // --------------------------------------------------

      const routeUrl =
        `https://router.project-osrm.org/route/v1/driving/` +
        `${start.longitude},${start.latitude};` +
        `${end.longitude},${end.latitude}` +
        `?overview=full&geometries=geojson&alternatives=false`

      const routeResponse = await fetch(routeUrl)

      if (!routeResponse.ok) {
        throw new Error('Unable to calculate the route.')
      }

      const routeData = await routeResponse.json()

      // Check again
      if (currentRequestId !== requestIdRef.current) return

      if (
        routeData.code !== 'Ok' ||
        !routeData.routes ||
        routeData.routes.length === 0
      ) {
        throw new Error(
          'No driving route could be found between these locations.'
        )
      }

      // Only use the FIRST recommended route
      const route = routeData.routes[0]

      // --------------------------------------------------
      // CLEAR ONE MORE TIME BEFORE DRAWING
      // --------------------------------------------------

      clearMap()

      // Check one final time
      if (currentRequestId !== requestIdRef.current) return

      // --------------------------------------------------
      // MARKERS
      // --------------------------------------------------

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

      L.marker(
        [start.latitude, start.longitude],
        {
          icon: pickupIcon,
        }
      )
        .bindPopup(`<b>Pickup</b><br>${pickup}`)
        .addTo(markerLayerRef.current)

      L.marker(
        [end.latitude, end.longitude],
        {
          icon: destinationIcon,
        }
      )
        .bindPopup(`<b>Destination</b><br>${destination}`)
        .addTo(markerLayerRef.current)

      // --------------------------------------------------
      // DRAW ONLY THE CURRENT ROUTE
      // --------------------------------------------------

      routeLayerRef.current = L.geoJSON(route.geometry, {
        style: {
          color: '#16a34a',
          weight: 6,
          opacity: 0.9,
        },
      }).addTo(mapRef.current)

      // --------------------------------------------------
      // ZOOM ONLY TO CURRENT ROUTE
      // --------------------------------------------------

      const bounds = routeLayerRef.current.getBounds()

      mapRef.current.fitBounds(bounds, {
        padding: [40, 40],
      })

      // --------------------------------------------------
      // ROUTE INFORMATION
      // --------------------------------------------------

      setDistance((route.distance / 1000).toFixed(1))
      setDuration(Math.round(route.duration / 60))

      setRouteReady(true)
    } catch (err) {
      // Ignore errors from old requests
      if (currentRequestId !== requestIdRef.current) return

      console.error(err)

      clearMap()

      setError(
        err.message ||
          'Could not load the route. Please check the locations.'
      )

      setRouteReady(false)
    } finally {
      // Only update loading state for the newest request
      if (currentRequestId === requestIdRef.current) {
        setLoading(false)
      }
    }
  }

  // --------------------------------------------------
  // GOOGLE MAPS
  // --------------------------------------------------

  const openGoogleMaps = () => {
    if (!pickup || !destination) return

    const googleMapsUrl =
      `https://www.google.com/maps/dir/?api=1` +
      `&origin=${encodeURIComponent(pickup)}` +
      `&destination=${encodeURIComponent(destination)}` +
      `&travelmode=driving`

    window.open(
      googleMapsUrl,
      '_blank',
      'noopener,noreferrer'
    )
  }

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="bg-white rounded-3xl border border-ink-200 shadow-lg shadow-ink-900/5 overflow-hidden">

      {/* HEADER */}

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

      {/* MAP */}

      <div className="relative">

        <div
          ref={mapContainerRef}
          className="w-full h-[430px]"
        />

        {/* STATUS */}

        <div className="absolute top-5 left-5 z-[500] bg-white rounded-full px-5 py-3 shadow-lg flex items-center gap-2">

          <span
            className={`w-3 h-3 rounded-full ${
              loading
                ? 'bg-yellow-400 animate-pulse'
                : error
                ? 'bg-red-500'
                : routeReady
                ? 'bg-green-500'
                : 'bg-gray-400'
            }`}
          />

          <span className="text-sm font-semibold text-ink-700">

            {loading
              ? 'LOADING ROUTE'
              : error
              ? 'ROUTE ERROR'
              : routeReady
              ? 'ROUTE READY'
              : 'ENTER LOCATIONS'}

          </span>

        </div>

        {/* ROUTE INFO */}

        <div className="absolute bottom-5 left-5 z-[500] bg-white rounded-2xl px-5 py-4 shadow-xl">

          <p className="text-xs font-semibold tracking-wider text-ink-400 uppercase">
            Route Preview
          </p>

          <p className="text-base font-semibold text-ink-900 mt-1">

            {loading
              ? 'Finding your route...'
              : error
              ? 'Route unavailable'
              : routeReady
              ? 'Ready to navigate'
              : 'Enter locations above'}

          </p>

        </div>

        {/* READY BADGE */}

        {routeReady && (

          <div className="absolute bottom-5 right-5 z-[500] bg-white border border-brand-200 rounded-full px-5 py-3 shadow-lg">

            <span className="text-sm font-semibold text-brand-600">
              RouteZero route
            </span>

          </div>

        )}

        {/* ERROR */}

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

      {/* BOTTOM INFORMATION */}

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