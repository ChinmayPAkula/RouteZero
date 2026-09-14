import {
  Bike,
  Truck,
  Van,
  Car,
  Check,
} from 'lucide-react'

import { vehicleOptions } from '../data/dummyData'

const icons = {
  two_wheeler: Bike,
  auto: Car,
  sedan: Car,
  suv: Car,
  mini_van: Van,
  truck: Truck,
}

export default function VehicleSelector({
  selected,
  onSelect,
}) {

  return (

    <div>

      <div className="flex items-center justify-between mb-3">

        <label className="text-sm font-semibold text-ink-800">
          Vehicle
        </label>

        <span className="text-[11px] text-ink-400">
          Select capacity
        </span>

      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">

        {vehicleOptions.map((vehicle) => {

          const Icon = icons[vehicle.id]
          const isSelected = selected === vehicle.id

          return (

            <button
              key={vehicle.id}
              type="button"
              onClick={() => onSelect(vehicle.id)}
              className={`
                relative text-left rounded-2xl border p-3.5
                transition-all duration-200
                ${
                  isSelected
                    ? 'border-brand-500 bg-brand-50 shadow-sm shadow-brand-500/10'
                    : 'border-ink-200 bg-white hover:border-ink-300 hover:-translate-y-0.5'
                }
              `}
            >

              {isSelected && (

                <div className="absolute top-2.5 right-2.5 w-5 h-5 rounded-full bg-brand-500 flex items-center justify-center">

                  <Check
                    size={12}
                    className="text-white"
                  />

                </div>

              )}

              <div
                className={`
                  w-9 h-9 rounded-xl flex items-center justify-center mb-3
                  ${
                    isSelected
                      ? 'bg-white text-brand-600'
                      : 'bg-ink-50 text-ink-500'
                  }
                `}
              >

                <Icon size={18} />

              </div>

              <p
                className={`
                  text-xs font-semibold
                  ${
                    isSelected
                      ? 'text-brand-800'
                      : 'text-ink-700'
                  }
                `}
              >
                {vehicle.label}
              </p>

              <p className="text-[10px] text-ink-400 mt-1">
                Up to {vehicle.capacityKg} kg
              </p>

            </button>

          )
        })}

      </div>

    </div>
  )
}