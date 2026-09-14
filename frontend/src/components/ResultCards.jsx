import {
  Route,
  Clock3,
  Leaf,
  TrendingDown,
} from 'lucide-react'


function ResultCard({
  icon,
  label,
  value,
  detail,
  highlight,
}) {

  return (

    <div
      className={`
        rounded-2xl border p-5 transition-all duration-200
        ${
          highlight
            ? 'border-brand-200 bg-brand-50/70'
            : 'border-ink-200 bg-white'
        }
        hover:-translate-y-0.5 hover:shadow-lg hover:shadow-ink-900/[0.05]
      `}
    >

      <div className="flex items-start justify-between">

        <div
          className={`
            w-9 h-9 rounded-xl flex items-center justify-center
            ${
              highlight
                ? 'bg-brand-500 text-white'
                : 'bg-ink-50 text-ink-500'
            }
          `}
        >
          {icon}
        </div>

        {highlight && (
          <span className="text-[9px] uppercase tracking-wider font-bold text-brand-600">
            Impact
          </span>
        )}

      </div>

      <p className="text-[11px] font-medium text-ink-400 mt-5">
        {label}
      </p>

      <p
        className={`
          text-2xl font-semibold tracking-tight mt-1
          ${
            highlight
              ? 'text-brand-800'
              : 'text-ink-900'
          }
        `}
      >
        {value}
      </p>

      <p className="text-[10px] text-ink-400 mt-1">
        {detail}
      </p>

    </div>
  )
}


export default function ResultCards({ result }) {

  const normalDistance =
    Number(result.normal_route.total_distance_km) || 0

  const optimizedDistance =
    Number(result.optimized_route.total_distance_km) || 0

  const normalTime =
    Number(result.normal_route.total_duration_minutes) || 0

  const optimizedTime =
    Number(result.optimized_route.total_duration_minutes) || 0

  const normalCO2 =
    Number(result.emissions.normal_route.co2_kg) || 0

  const optimizedCO2 =
    Number(result.emissions.route_zero.co2_kg) || 0

  const distanceSaved =
    normalDistance - optimizedDistance

  const timeSaved =
    normalTime - optimizedTime

  const co2Saved =
    Number(
      result.emissions.metrics_comparison?.co2_saved_kg
    ) || (normalCO2 - optimizedCO2)


  return (

    <div>

      <div className="flex items-end justify-between mb-4">

        <div>

          <p className="text-[10px] uppercase tracking-[0.16em] font-bold text-brand-600">
            Optimization result
          </p>

          <h3 className="text-xl font-semibold tracking-tight text-ink-900 mt-1">
            Your greener route
          </h3>

        </div>

        <span className="hidden sm:block text-xs text-ink-400">
          Compared with standard routing
        </span>

      </div>


      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">

        <ResultCard
          icon={<Route size={18} />}
          label="DISTANCE"
          value={`${optimizedDistance.toFixed(1)} km`}
          detail={`${Math.max(distanceSaved, 0).toFixed(1)} km shorter`}
        />


        <ResultCard
          icon={<Clock3 size={18} />}
          label="ESTIMATED TIME"
          value={`${Math.round(optimizedTime)} min`}
          detail={`${Math.max(Math.round(timeSaved), 0)} min faster`}
        />


        <ResultCard
          icon={<Leaf size={18} />}
          label="CO₂ EMITTED"
          value={`${optimizedCO2.toFixed(2)} kg`}
          detail="Estimated emissions"
        />


        <ResultCard
          icon={<TrendingDown size={18} />}
          label="CO₂ SAVED"
          value={`${co2Saved.toFixed(2)} kg`}
          detail="Lower than standard route"
          highlight
        />

      </div>

    </div>
  )
}