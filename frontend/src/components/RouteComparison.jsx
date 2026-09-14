import {
  ArrowRight,
  Leaf,
  Clock3,
  Route,
  TrendingDown,
} from 'lucide-react'


export default function RouteComparison({ result }) {

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

  const backendCO2Percent =
    Number(
      result.emissions.metrics_comparison?.co2_percentage_reduction
    )

  const co2Percent = Number.isFinite(backendCO2Percent)
    ? backendCO2Percent.toFixed(1)
    : normalCO2 > 0
    ? ((co2Saved / normalCO2) * 100).toFixed(1)
    : '0.0'

  const distancePercent =
    normalDistance > 0
      ? ((distanceSaved / normalDistance) * 100).toFixed(1)
      : '0.0'

  const timePercent =
    normalTime > 0
      ? ((timeSaved / normalTime) * 100).toFixed(1)
      : '0.0'


  return (

    <section className="rounded-[28px] border border-ink-200 bg-white shadow-xl shadow-ink-900/[0.05] overflow-hidden">

      <div className="p-6 sm:p-8">

        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-7">

          <div>

            <div className="flex items-center gap-2 mb-2">

              <div className="w-7 h-7 rounded-lg bg-brand-50 flex items-center justify-center">

                <TrendingDown
                  size={14}
                  className="text-brand-600"
                />

              </div>

              <p className="text-[10px] uppercase tracking-[0.16em] font-bold text-brand-600">
                Route comparison
              </p>

            </div>

            <h3 className="text-2xl font-semibold tracking-tight text-ink-900">
              The difference is measurable.
            </h3>

            <p className="text-sm text-ink-400 mt-1">
              Standard routing vs. RouteZero optimization.
            </p>

          </div>

          <div className="flex items-center gap-2 rounded-full bg-brand-50 border border-brand-100 px-3 py-2">

            <Leaf
              size={14}
              className="text-brand-600"
            />

            <span className="text-xs font-bold text-brand-700">
              {co2Percent}% less CO₂
            </span>

          </div>

        </div>


        <div className="rounded-2xl border border-ink-100 overflow-hidden">

          <div className="grid grid-cols-[1fr_40px_1fr] bg-ink-50/70">

            <div className="px-4 sm:px-6 py-3">

              <span className="text-[10px] uppercase tracking-wider font-bold text-ink-400">
                Standard route
              </span>

            </div>

            <div />

            <div className="px-4 sm:px-6 py-3">

              <span className="text-[10px] uppercase tracking-wider font-bold text-brand-600">
                RouteZero
              </span>

            </div>

          </div>


          <div className="grid grid-cols-[1fr_40px_1fr] items-center border-t border-ink-100">

            <div className="px-4 sm:px-6 py-5">

              <div className="flex items-center gap-2 mb-1">

                <Route
                  size={14}
                  className="text-ink-400"
                />

                <span className="text-[10px] text-ink-400">
                  Distance
                </span>

              </div>

              <p className="text-lg font-semibold text-ink-800">
                {normalDistance.toFixed(1)} km
              </p>

            </div>

            <ArrowRight
              size={16}
              className="text-ink-300 mx-auto"
            />

            <div className="px-4 sm:px-6 py-5 bg-brand-50/40">

              <p className="text-lg font-semibold text-brand-700">
                {optimizedDistance.toFixed(1)} km
              </p>

              <p className="text-[10px] font-semibold text-brand-600 mt-1">
                {distancePercent}% shorter
              </p>

            </div>

          </div>


          <div className="grid grid-cols-[1fr_40px_1fr] items-center border-t border-ink-100">

            <div className="px-4 sm:px-6 py-5">

              <div className="flex items-center gap-2 mb-1">

                <Clock3
                  size={14}
                  className="text-ink-400"
                />

                <span className="text-[10px] text-ink-400">
                  Delivery time
                </span>

              </div>

              <p className="text-lg font-semibold text-ink-800">
                {Math.round(normalTime)} min
              </p>

            </div>

            <ArrowRight
              size={16}
              className="text-ink-300 mx-auto"
            />

            <div className="px-4 sm:px-6 py-5 bg-brand-50/40">

              <p className="text-lg font-semibold text-brand-700">
                {Math.round(optimizedTime)} min
              </p>

              <p className="text-[10px] font-semibold text-brand-600 mt-1">
                {timePercent}% faster
              </p>

            </div>

          </div>


          <div className="grid grid-cols-[1fr_40px_1fr] items-center border-t border-ink-100">

            <div className="px-4 sm:px-6 py-5">

              <div className="flex items-center gap-2 mb-1">

                <Leaf
                  size={14}
                  className="text-ink-400"
                />

                <span className="text-[10px] text-ink-400">
                  CO₂ emissions
                </span>

              </div>

              <p className="text-lg font-semibold text-ink-800">
                {normalCO2.toFixed(2)} kg
              </p>

            </div>

            <ArrowRight
              size={16}
              className="text-ink-300 mx-auto"
            />

            <div className="px-4 sm:px-6 py-5 bg-brand-50/40">

              <p className="text-lg font-semibold text-brand-700">
                {optimizedCO2.toFixed(2)} kg
              </p>

              <p className="text-[10px] font-semibold text-brand-600 mt-1">
                {co2Percent}% lower
              </p>

            </div>

          </div>

        </div>


        <div className="mt-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 rounded-2xl bg-ink-900 px-5 py-4">

          <div className="flex items-center gap-3">

            <div className="w-9 h-9 rounded-xl bg-brand-500/15 flex items-center justify-center">

              <Leaf
                size={16}
                className="text-brand-300"
              />

            </div>

            <div>

              <p className="text-xs font-semibold text-white">
                Carbon impact
              </p>

              <p className="text-[10px] text-ink-400 mt-0.5">
                Every optimized journey reduces unnecessary emissions.
              </p>

            </div>

          </div>

          <p className="text-xl font-semibold text-brand-300">
            {co2Saved.toFixed(2)} kg saved
          </p>

        </div>

      </div>

    </section>
  )
}