import {
  MapPin,
  Navigation,
  Sparkles,
  Plus,
  X,
} from 'lucide-react'

import VehicleSelector from './VehicleSelector'

export default function DeliveryForm({
  formData,
  setFormData,
  onOptimize,
  loading,
}) {

  const handleChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value,
    })
  }

  const addStop = () => {
    setFormData({
      ...formData,
      stops: [...formData.stops, ''],
    })
  }

  const updateStop = (index, value) => {
    const newStops = [...formData.stops]
    newStops[index] = value

    setFormData({
      ...formData,
      stops: newStops,
    })
  }

  const removeStop = (index) => {
    const newStops = formData.stops.filter(
      (_, i) => i !== index
    )

    setFormData({
      ...formData,
      stops: newStops,
    })
  }

  return (
    <div className="bg-white rounded-2xl border border-ink-200 p-6 shadow-lg shadow-ink-900/5 space-y-5">

      <h2 className="text-lg font-semibold text-ink-900">
        Delivery Details
      </h2>

      <div>
        <label className="block text-sm font-medium text-ink-600 mb-2">
          Pickup Location
        </label>

        <div className="relative">

          <MapPin
            className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-500"
            size={18}
          />

          <input
            type="text"
            value={formData.pickup}
            onChange={(e) =>
              handleChange('pickup', e.target.value)
            }
            placeholder="Enter pickup address"
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-ink-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
          />

        </div>
      </div>

      <div>

        <div className="flex items-center justify-between mb-2">

          <label className="block text-sm font-medium text-ink-600">
            Stops
          </label>

          <button
            type="button"
            onClick={addStop}
            className="flex items-center gap-1 text-xs font-semibold text-brand-600 hover:text-brand-700"
          >
            <Plus size={14} />
            Add stop
          </button>

        </div>

        {formData.stops.length === 0 && (
          <p className="text-xs text-ink-400">
            Add delivery stops if your route has multiple destinations.
          </p>
        )}

        <div className="space-y-2">

          {formData.stops.map((stop, index) => (

            <div
              key={index}
              className="relative flex items-center gap-2"
            >

              <div className="relative flex-1">

                <Navigation
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-500"
                  size={17}
                />

                <input
                  type="text"
                  value={stop}
                  onChange={(e) =>
                    updateStop(index, e.target.value)
                  }
                  placeholder={`Enter stop ${index + 1}`}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-ink-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                />

              </div>

              <button
                type="button"
                onClick={() => removeStop(index)}
                className="w-9 h-9 rounded-xl border border-ink-200 flex items-center justify-center text-ink-400 hover:text-red-500 hover:border-red-200 transition"
              >
                <X size={16} />
              </button>

            </div>

          ))}

        </div>

      </div>

      <div>

        <label className="block text-sm font-medium text-ink-600 mb-2">
          Drop Location
        </label>

        <div className="relative">

          <Navigation
            className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-500"
            size={18}
          />

          <input
            type="text"
            value={formData.drop}
            onChange={(e) =>
              handleChange('drop', e.target.value)
            }
            placeholder="Enter drop address"
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-ink-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
          />

        </div>

      </div>

      <VehicleSelector
        selected={formData.vehicle}
        onSelect={(id) =>
          handleChange('vehicle', id)
        }
      />

      <div>

        <label className="block text-sm font-medium text-ink-600 mb-2">
          Fuel Type
        </label>

        <select
          value={formData.fuelType}
          onChange={(e) =>
            handleChange('fuelType', e.target.value)
          }
          className="w-full px-4 py-2.5 rounded-xl border border-ink-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition text-sm text-ink-700"
        >
          <option value="petrol">Petrol</option>
          <option value="diesel">Diesel</option>
          <option value="electric">Electric</option>
          <option value="cng">CNG</option>
        </select>

      </div>

      <button
        onClick={onOptimize}
        disabled={loading}
        className="w-full bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium py-3 rounded-xl transition shadow-md shadow-brand-500/30 hover:shadow-lg hover:shadow-brand-500/40 flex items-center justify-center gap-2 hover:-translate-y-0.5 active:translate-y-0"
      >

        <Sparkles size={18} />

        {loading
          ? 'Optimizing Route...'
          : 'Optimize Route'}

      </button>

    </div>
  )
}