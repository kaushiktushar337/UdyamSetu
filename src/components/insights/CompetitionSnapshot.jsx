import { Gauge } from 'lucide-react'

export default function CompetitionSnapshot() {
  return (
    <div className="soft-card p-5">
      <div className="flex items-center justify-between gap-4">
        <div className="text-sm font-semibold text-neutral-900">Competition Snapshot</div>
        <Gauge size={17} className="text-udyam-700" />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-neutral-50 p-3">
          <div className="text-[10px] text-neutral-500">Existing dairy businesses</div>
          <div className="mt-1 text-lg font-bold">12</div>
        </div>
        <div className="rounded-xl bg-neutral-50 p-3">
          <div className="text-[10px] text-neutral-500">Competition level</div>
          <div className="mt-1 text-sm font-semibold text-amber-600">Medium</div>
        </div>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between text-[11px] text-neutral-500">
          <span>Market Saturation</span>
          <span className="font-semibold text-neutral-800">48%</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-neutral-100">
          <div className="h-full w-[48%] rounded-full bg-udyam-500" />
        </div>
      </div>
    </div>
  )
}
