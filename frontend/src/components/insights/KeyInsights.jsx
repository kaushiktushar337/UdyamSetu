import { CheckCircle2 } from 'lucide-react'

export default function KeyInsights({ data }) {
  const best = data.mlBusinessMatches?.[0]
  const bullets = [
    best ? `${best.business_name} is the strongest business match for the selected category.` : 'No business match is available yet for this location.',
    data.opportunityScore != null ? `The local opportunity score is ${Number(data.opportunityScore).toFixed(0)}/100.` : 'Opportunity scoring is not available for this area yet.',
    data.competitionScore != null ? `Competition is currently rated ${data.competitionScore >= 70 ? 'high' : data.competitionScore >= 40 ? 'medium' : 'low'} by the stored market metric.` : 'Competition data is not available yet.',
  ]
  return <div className="soft-card p-5"><div className="text-sm font-semibold text-neutral-900">Key insights</div><div className="mt-4 grid gap-3">{bullets.map((bullet) => <div key={bullet} className="flex gap-2 text-xs leading-5 text-neutral-700"><CheckCircle2 size={15} className="mt-0.5 shrink-0 text-udyam-600" />{bullet}</div>)}</div>{data.dataDate && <div className="mt-4 text-[10px] text-neutral-500">Market metrics date: {data.dataDate}</div>}</div>
}
