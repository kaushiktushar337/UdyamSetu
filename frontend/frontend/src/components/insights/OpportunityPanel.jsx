import { CheckCircle2, Sparkles } from 'lucide-react'

export default function OpportunityPanel({ data }) {
  return (
    <div className="soft-card p-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900"><Sparkles size={16} className="text-udyam-700" /> Demand & opportunity</div>
      <p className="mt-2 text-xs leading-5 text-neutral-600">The selected area has a demand score of <strong>{data.demandScore == null ? '—' : Number(data.demandScore).toFixed(0)}/100</strong> and an opportunity score of <strong>{data.opportunityScore == null ? '—' : Number(data.opportunityScore).toFixed(0)}/100</strong>.</p>
      <div className="mt-4 inline-flex rounded-full bg-udyam-50 px-3 py-1 text-[10px] font-semibold text-udyam-700">Best match</div>
      <div className="mt-4 grid gap-3">
        {(data.mlBusinessMatches.length ? data.mlBusinessMatches : data.topOpportunities).slice(0, 5).map((item, index) => {
          const name = typeof item === 'string' ? item : item.business_name
          const score = typeof item === 'object' ? item.semantic_score : null
          return <div key={`${name}-${index}`} className="flex items-center justify-between gap-3 text-xs text-neutral-700"><span className="flex items-center gap-2"><CheckCircle2 size={15} className="shrink-0 text-udyam-600" />{name}</span>{score != null && <span className="font-semibold text-udyam-700">{(Number(score) * 100).toFixed(0)}%</span>}</div>
        })}
        {!data.mlBusinessMatches.length && !data.topOpportunities.length && <p className="text-xs text-neutral-500">No matching opportunities are available for this area yet.</p>}
      </div>
    </div>
  )
}
