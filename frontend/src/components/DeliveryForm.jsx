import {
  MapPin,
  Navigation,
  ArrowDown,
  Sparkles,
} from 'lucide-react'

import VehicleSelector from './VehicleSelector'


export default function DeliveryForm({
  formData,
  setFormData,
  onOptimize,
}) {

  const handleChange = (field, value) => {

    setFormData({
      ...formData,
      [field]: value,
    })

  }


  return (

    <section className="relative overflow-hidden rounded-[30px] border border-ink-200 bg-white shadow-xl shadow-ink-900/[0.06]">

      <div className="absolute top-0 right-0 w-72 h-72 rounded-full bg-brand-100/40 blur-3xl pointer-events-none" />


      <div className="relative p-6 sm:p-8">


        {/* Heading */}

        <div className="mb-7">

          <div className="flex items-center gap-2 mb-3">

            <span className="flex items-center gap-1.5 rounded-full bg-brand-50 border border-brand-100 px-2.5 py-1">

              <span className="w-1.5 h-1.5 rounded-full bg-brand-500" />

              <span className="text-[10px] font-bold uppercase tracking-wider text-brand-700">
                Route planner
              </span>

            </span>

          </div>


          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-ink-900">
            Plan your delivery.
          </h2>

          <p className="text-sm text-ink-400 mt-1.5">
            Enter your journey details and let RouteZero find a more efficient route.
          </p>

        </div>


        {/* Locations */}

        <div className="grid md:grid-cols-[1fr_auto_1fr] items-end gap-3">


          <div>

            <label className="block text-xs font-semibold text-ink-600 mb-2">
              Pickup location
            </label>

            <div className="relative">

              <MapPin
                size={17}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400"
              />

              <input
                type="text"
                value={formData.pickup}
                onChange={(e) =>
                  handleChange('pickup', e.target.value)
                }
                placeholder="Enter pickup location"
                className="w-full h-12 rounded-xl border border-ink-200 bg-ink-50/50 pl-10 pr-4 text-sm text-ink-800 placeholder:text-ink-400 outline-none transition focus:border-brand-400 focus:bg-white focus:ring-4 focus:ring-brand-500/10"
              />

            </div>

          </div>


          {/* Connector */}

          <div className="hidden md:flex items-center justify-center pb-2">

            <div className="w-9 h-9 rounded-full border border-ink-200 bg-white flex items-center justify-center">

              <ArrowDown
                size={15}
                className="text-ink-400 rotate-[-90deg]"
              />

            </div>

          </div>


          <div>

            <label className="block text-xs font-semibold text-ink-600 mb-2">
              Destination
            </label>

            <div className="relative">

              <Navigation
                size={17}
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-brand-600"
              />

              <input
                type="text"
                value={formData.drop}
                onChange={(e) =>
                  handleChange('drop', e.target.value)
                }
                placeholder="Enter destination"
                className="w-full h-12 rounded-xl border border-ink-200 bg-ink-50/50 pl-10 pr-4 text-sm text-ink-800 placeholder:text-ink-400 outline-none transition focus:border-brand-400 focus:bg-white focus:ring-4 focus:ring-brand-500/10"
              />

            </div>

          </div>

        </div>


        {/* Divider */}

        <div className="h-px bg-ink-100 my-7" />


        {/* Vehicle */}

        <VehicleSelector
          selected={formData.vehicle}
          onSelect={(id) =>
            handleChange('vehicle', id)
          }
        />


        {/* Button */}

        <button
          type="button"
          onClick={onOptimize}
          className="group mt-7 w-full h-13 rounded-xl bg-ink-900 text-white font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200 hover:bg-ink-800 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-ink-900/15 active:translate-y-0"
        >

          <Sparkles
            size={17}
            className="text-brand-300 transition-transform group-hover:rotate-12"
          />

          Optimize Route

          <span className="text-ink-400 group-hover:text-brand-300 transition">
            →
          </span>

        </button>


        <p className="text-center text-[10px] text-ink-400 mt-3">
          Optimization currently uses demonstration data
        </p>

      </div>

    </section>
  )
}