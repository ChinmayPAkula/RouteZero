import { useState } from 'react'

import Header from './components/Header'
import DeliveryForm from './components/DeliveryForm'
import ResultCards from './components/ResultCards'
import RouteMap from './components/RouteMap'
import RouteComparison from './components/RouteComparison'

import { dummyResult } from './data/dummyData'


export default function App() {

  const [formData, setFormData] = useState({
    pickup: '',
    drop: '',
    vehicle: 'van',
  })


  const [showResults, setShowResults] = useState(false)


  const handleOptimize = () => {
    setShowResults(true)
  }


  return (

    <div className="min-h-screen">

      <Header />


      <main className="max-w-6xl mx-auto px-5 sm:px-6 py-8 sm:py-10">


        {/* Intro */}

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


        {/* Planner */}

        <DeliveryForm
          formData={formData}
          setFormData={setFormData}
          onOptimize={handleOptimize}
        />


        {/* Results */}

        {showResults && (

          <div className="mt-10 space-y-8 animate-fade-in-up">


            {/* Result heading */}

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


            {/* Stats */}

            <ResultCards
              result={dummyResult}
            />


            {/* Map */}

            <RouteMap />


            {/* Comparison */}

            <RouteComparison
              result={dummyResult}
            />


          </div>

        )}

      </main>

    </div>
  )
}