import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Popup,
  useMap,
} from 'react-leaflet'

import { useEffect } from 'react'

import {
  Navigation,
  Leaf,
  Map,
} from 'lucide-react'

import { dummyResult } from '../data/dummyData'

import 'leaflet/dist/leaflet.css'


function FitRoute() {

  const map = useMap()

  useEffect(() => {

    map.fitBounds(
      dummyResult.routeCoordinates,
      {
        padding: [50, 50],
      }
    )

  }, [map])

  return null
}


export default function RouteMap() {

  return (

    <section className="overflow-hidden rounded-[28px] border border-ink-200 bg-white shadow-xl shadow-ink-900/[0.05]">


      {/* Header */}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-6 py-5 border-b border-ink-100">

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-xl bg-ink-900 flex items-center justify-center">

            <Map
              size={18}
              className="text-brand-400"
            />

          </div>


          <div>

            <p className="text-[10px] uppercase tracking-[0.16em] font-bold text-brand-600">
              Route visualization
            </p>

            <h3 className="text-base font-semibold text-ink-900 mt-0.5">
              Optimized delivery path
            </h3>

          </div>

        </div>


        <div className="flex items-center gap-4 text-[11px] text-ink-500">

          <div className="flex items-center gap-1.5">

            <span className="w-2.5 h-2.5 rounded-full bg-ink-800 border-2 border-white shadow" />

            Pickup

          </div>


          <div className="flex items-center gap-1.5">

            <span className="w-2.5 h-2.5 rounded-full bg-brand-500 border-2 border-white shadow" />

            Destination

          </div>

        </div>

      </div>


      {/* Map */}

      <div className="relative h-[400px]">

        <MapContainer
          center={[12.943, 77.618]}
          zoom={12}
          scrollWheelZoom={false}
          className="h-full w-full"
        >

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          <FitRoute />


          {/* Route shadow */}

          <Polyline
            positions={dummyResult.routeCoordinates}
            pathOptions={{
              color: '#0f172a',
              weight: 10,
              opacity: 0.12,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />


          {/* Route */}

          <Polyline
            positions={dummyResult.routeCoordinates}
            pathOptions={{
              color: '#16a34a',
              weight: 5,
              opacity: 1,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />


          {/* Intermediate points */}

          {dummyResult.routeCoordinates
            .slice(1, -1)
            .map((coordinate, index) => (

              <CircleMarker
                key={index}
                center={coordinate}
                radius={4}
                pathOptions={{
                  color: '#ffffff',
                  weight: 2,
                  fillColor: '#16a34a',
                  fillOpacity: 1,
                }}
              />

            ))}


          {/* Pickup */}

          <CircleMarker
            center={dummyResult.routeCoordinates[0]}
            radius={9}
            pathOptions={{
              color: '#ffffff',
              weight: 4,
              fillColor: '#0f172a',
              fillOpacity: 1,
            }}
          >

            <Popup>
              <strong>Pickup</strong>
              <br />
              Bengaluru
            </Popup>

          </CircleMarker>


          {/* Destination */}

          <CircleMarker
            center={
              dummyResult.routeCoordinates[
                dummyResult.routeCoordinates.length - 1
              ]
            }
            radius={9}
            pathOptions={{
              color: '#ffffff',
              weight: 4,
              fillColor: '#16a34a',
              fillOpacity: 1,
            }}
          >

            <Popup>
              <strong>Destination</strong>
              <br />
              Bengaluru
            </Popup>

          </CircleMarker>

        </MapContainer>


        {/* Status */}

        <div className="absolute top-4 left-4 z-[1000]">

          <div className="flex items-center gap-2 rounded-full border border-white/70 bg-white/90 backdrop-blur-xl px-3 py-2 shadow-lg">

            <span className="relative flex w-2 h-2">

              <span className="absolute w-full h-full rounded-full bg-brand-400 animate-ping" />

              <span className="relative w-2 h-2 rounded-full bg-brand-500" />

            </span>

            <span className="text-[10px] font-bold text-ink-700">
              ROUTE OPTIMIZED
            </span>

          </div>

        </div>


        {/* Summary */}

        <div className="absolute bottom-4 left-4 z-[1000]">

          <div className="rounded-2xl border border-white/70 bg-white/90 backdrop-blur-xl px-4 py-3 shadow-xl">

            <div className="flex items-center gap-3">

              <div className="w-9 h-9 rounded-xl bg-brand-50 flex items-center justify-center">

                <Navigation
                  size={16}
                  className="text-brand-600"
                />

              </div>


              <div>

                <p className="text-[9px] uppercase tracking-wider font-bold text-ink-400">
                  Optimized journey
                </p>

                <p className="text-sm font-bold text-ink-900">
                  36.1 km · 61 min
                </p>

              </div>

            </div>

          </div>

        </div>


        {/* CO2 */}

        <div className="absolute bottom-4 right-4 z-[1000]">

          <div className="flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50/95 backdrop-blur-xl px-3.5 py-2.5 shadow-lg">

            <Leaf
              size={15}
              className="text-brand-600"
            />

            <span className="text-[11px] font-bold text-brand-700">
              26.5% lower CO₂
            </span>

          </div>

        </div>

      </div>


      {/* Map footer */}

      <div className="grid grid-cols-3 border-t border-ink-100 bg-ink-50/50">

        <div className="px-5 py-4 border-r border-ink-100">

          <p className="text-[9px] uppercase tracking-wider font-bold text-ink-400">
            Distance
          </p>

          <p className="text-sm font-semibold text-ink-900 mt-1">
            36.1 km
          </p>

        </div>


        <div className="px-5 py-4 border-r border-ink-100">

          <p className="text-[9px] uppercase tracking-wider font-bold text-ink-400">
            Time
          </p>

          <p className="text-sm font-semibold text-ink-900 mt-1">
            61 min
          </p>

        </div>


        <div className="px-5 py-4">

          <p className="text-[9px] uppercase tracking-wider font-bold text-ink-400">
            Emissions
          </p>

          <p className="text-sm font-semibold text-brand-600 mt-1">
            7.2 kg CO₂
          </p>

        </div>

      </div>

    </section>
  )
}