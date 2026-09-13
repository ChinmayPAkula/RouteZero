import { Leaf, ArrowUpRight } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-ink-200/70 bg-white/85 backdrop-blur-xl">

      <div className="max-w-6xl mx-auto px-5 sm:px-6">

        <div className="h-[72px] flex items-center justify-between">

          <div className="flex items-center gap-3">

            <div className="relative w-10 h-10 rounded-xl bg-ink-900 flex items-center justify-center shadow-lg shadow-ink-900/10">

              <Leaf
                size={19}
                className="text-brand-400"
              />

              <span className="absolute -right-1 -top-1 w-2.5 h-2.5 rounded-full bg-brand-500 border-2 border-white" />

            </div>

            <div>
              <h1 className="text-[17px] font-bold tracking-tight text-ink-900">
                RouteZero
              </h1>

              <p className="text-[10px] text-ink-400 tracking-wide">
                LOW-CARBON LOGISTICS
              </p>
            </div>

          </div>


          <div className="hidden sm:flex items-center gap-5">

            <span className="text-xs font-medium text-ink-400">
              Intelligent routing
            </span>

            <div className="h-4 w-px bg-ink-200" />

            <div className="flex items-center gap-1.5 text-xs font-semibold text-brand-700">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-500" />
              System ready
            </div>

            <ArrowUpRight
              size={15}
              className="text-ink-300"
            />

          </div>

        </div>

      </div>

    </header>
  )
}