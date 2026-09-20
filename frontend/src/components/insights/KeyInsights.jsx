import { CheckCircle2 } from 'lucide-react'

function level(score) {
  if (score == null) return 'not available'
  if (score >= 70) return 'high'
  if (score >= 40) return 'moderate'
  return 'low'
}

export default function KeyInsights({ data }) {
  const best = data.topOpportunities?.[0]
  const bullets = [
    best
      ? `${best.business_name} has the strongest opportunity signal for the selected category and area.`
      : 'No specific business opportunity is available yet for this area.',
    data.opportunityScore != null
      ? `The combined opportunity score is ${Number(data.opportunityScore).toFixed(0)}/100.`
      : 'Opportunity scoring is not available for this area yet.',
    data.competitionScore != null
      ? `Relative competition is ${level(data.competitionScore)} (${Number(data.competitionScore).toFixed(0)}/100).`
      : 'Competition data is not available yet.',
    data.localEnvironmentScore != null
      ? `The local business environment scores ${Number(data.localEnvironmentScore).toFixed(0)}/100 and is used as supporting context.`
      : 'Additional local business-environment context is not available for this area yet.',
  ]

  return (
    <div className="soft-card p-5">
      <div className="text-sm font-semibold text-neutral-900">Key insights</div>
      <div className="mt-4 grid gap-3">
        {bullets.map((bullet) => (
          <div key={bullet} className="flex gap-2 text-xs leading-5 text-neutral-700">
            <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-udyam-600" />
            {bullet}
          </div>
        ))}
      </div>
      {data.dataDate && <div className="mt-4 text-[10px] text-neutral-500">Market update: {data.dataDate}</div>}
    </div>
  )
}
