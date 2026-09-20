import { CheckCircle2 } from 'lucide-react'

function level(score) {
  if (score == null) return 'not available'
  if (score >= 70) return 'high'
  if (score >= 40) return 'moderate'
  return 'low'
}

export default function KeyInsights({ data }) {
  const bullets = []
  const demand = data.demandScore == null ? null : Number(data.demandScore)
  const competition = data.competitionScore == null ? null : Number(data.competitionScore)
  const opportunity = data.opportunityScore == null ? null : Number(data.opportunityScore)

  if (demand != null && competition != null) {
    if (demand >= 70 && competition < 70) bullets.push('Demand indicators are relatively strong while competitive pressure remains below the high range.')
    else if (competition >= 70) bullets.push('Competitive pressure is relatively high, so differentiation may require additional planning.')
    else bullets.push(`Demand is ${level(demand)} and relative competition is ${level(competition)} for this local category.`)
  } else if (demand != null) {
    bullets.push(`Local demand is ${level(demand)} (${demand.toFixed(0)}/100).`)
  }

  if (opportunity != null) {
    if (opportunity >= 70) bullets.push(`The available market indicators show a relatively strong opportunity signal at ${opportunity.toFixed(0)}/100.`)
    else if (opportunity >= 40) bullets.push(`The available market indicators suggest a moderate opportunity; validate local demand before committing significant capital.`)
    else bullets.push(`The available market indicators show a lower opportunity signal at ${opportunity.toFixed(0)}/100.`)
  }

  if (data.localEnvironmentScore != null) {
    bullets.push(`The local business environment is ${level(Number(data.localEnvironmentScore))} (${Number(data.localEnvironmentScore).toFixed(0)}/100) and is used as supporting context.`)
  }

  if (!bullets.length) bullets.push('There is not enough local market data to generate a reliable insight yet.')

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
