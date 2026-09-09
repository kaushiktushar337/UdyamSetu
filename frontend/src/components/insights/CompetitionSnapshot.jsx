import { Gauge } from 'lucide-react'

function level(score) {
  if (score == null) return 'Not available'
  if (score >= 70) return 'High'
  if (score >= 40) return 'Medium'
  return 'Low'
}

export default function CompetitionSnapshot({ data }) {
  const saturation = data.competitionScore == null ? 0 : Math.max(0, Math.min(100, Number(data.competitionScore)))
  return (
    <div className="soft-card p-5">
      <div className="flex items-center justify-between gap-4"><div className="text-sm font-semibold text-neutral-900">Competition snapshot</div><Gauge size={17} className="text-udyam-700" /></div>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-neutral-50 p-3"><div className="text-[10px] text-neutral-500">Existing businesses</div><div className="mt-1 text-lg font-bold">{data.competitionCount ?? '—'}</div></div>
        <div className="rounded-xl bg-neutral-50 p-3"><div className="text-[10px] text-neutral-500">Competition level</div><div className="mt-1 text-sm font-semibold text-amber-600">{level(data.competitionScore)}</div></div>
      </div>
      <div className="mt-5"><div className="flex items-center justify-between text-[11px] text-neutral-500"><span>Competition score</span><span className="font-semibold text-neutral-800">{data.competitionScore == null ? '—' : `${Number(data.competitionScore).toFixed(0)}/100`}</span></div><div className="mt-2 h-2 rounded-full bg-neutral-100"><div className="h-full rounded-full bg-udyam-500 transition-all" style={{ width: `${saturation}%` }} /></div></div>
    </div>
  )
}
