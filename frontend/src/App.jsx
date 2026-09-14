import { useRef, useState } from 'react'

import Header from './components/Header'
import DeliveryForm from './components/DeliveryForm'
import ResultCards from './components/ResultCards'
import RouteMap from './components/RouteMap'
import RouteComparison from './components/RouteComparison'

const API_URL = 'http://127.0.0.1:8000/plan-route'

export default function App() {
  const [formData, setFormData] = useState({
    pickup: '',
    stops: [],
    drop: '',
    vehicle: 'two_wheeler',
    fuelType: 'petrol',
  })

  const [showResults, setShowResults] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const resultsRef = useRef(null)

  const handleOptimize = async () => {
    if (!formData.pickup.trim() || !formData.drop.trim()) {
      setError('Please enter both pickup and destination.')
      return
    }

    setLoading(true)
    setError('')
    setShowResults(false)
    setResult(null)

    const payload = {
      pickup_location: formData.pickup,
      stops: formData.stops.filter(
        (stop) => stop && stop.trim()
      ),
      destination: formData.drop,
      vehicle_class: formData.vehicle,
      fuel_type: formData.fuelType,
    }

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let message = 'Unable to optimize the route.'

        try {
          const errorData = await response.json()

          if (errorData.detail) {
            message =
              typeof errorData.detail === 'string'
                ? errorData.detail
                : 'Backend rejected the route request.'
          }
        } catch {
          // Keep default error message
        }

        throw new Error(message)
      }

      const data = await response.json()

      if (
        !data.normal_route ||
        !data.optimized_route ||
        !data.emissions
      ) {
        throw new Error(
          'The backend returned an unexpected response.'
        )
      }

      setResult(data)
      setShowResults(true)

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        })
      }, 100)

    } catch (err) {
      console.error('Route optimization error:', err)

      if (err instanceof TypeError) {
        setError(
          'Failed to connect to the backend. Make sure Khanak\'s backend is running on port 8000.'
        )
      } else {
        setError(
          err.message ||
            'Something went wrong while optimizing the route.'
        )
      }

    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">

      <Header />

      <main className="max-w-6xl mx-auto px-5 sm:px-6 py-8 sm:py-10">

        <div className="max-w-3xl mb-7">

          <p className="text-[10px] uppercase tracking-[0.18em] font-bold text-brand-600">
            Sustainable logistics
          </p>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-[-0.03em] text-ink-900 mt-2">
            Plan smarter.
            <span className="text-brand-600"> Deliver greener.</span>
          </h2>

          <p className="text-sm sm:text-base text-ink-400 leading-6 mt-3 max-w-2xl">
            Optimize delivery routes for lower travel distance,
            faster journeys and reduced carbon emissions.
          </p>

        </div>

        <DeliveryForm
          formData={formData}
          setFormData={setFormData}
          onOptimize={handleOptimize}
          loading={loading}
        />

        {error && (
          <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
            <p className="text-sm font-semibold text-red-600">
              {error}
            </p>
          </div>
        )}

        {showResults && result && (
          <div
            ref={resultsRef}
            className="mt-10 space-y-8 animate-fade-in-up"
          >

            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">

              <div>

                <p className="text-[10px] uppercase tracking-[0.16em] font-bold text-brand-600">
                  Optimization complete
                </p>

                <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-ink-900 mt-1">
                  Your route is ready.
                </h2>

              </div>

              <div className="flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1.5 self-start sm:self-auto">

                <span className="w-1.5 h-1.5 rounded-full bg-brand-500" />

                <span className="text-[10px] font-bold uppercase tracking-wider text-brand-700">
                  Optimized
                </span>

              </div>

            </div>

            <ResultCards result={result} />

            <RouteMap
              pickup={formData.pickup}
              stops={formData.stops}
              destination={formData.drop}
              routeData={result.optimized_route}
            />

            <RouteComparison result={result} />

          </div>
        )}

      </main>

    </div>
  )
}