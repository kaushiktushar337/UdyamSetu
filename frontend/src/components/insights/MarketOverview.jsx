import { Gauge, TrendingUp, IndianRupee, Users } from 'lucide-react'
import MetricCard from '../common/MetricCard'

function score(value) {
  return value == null ? '—' : `${Number(value).toFixed(0)}/100`
}

function price(value) {
  if (value == null) return 'Not available'
  return `₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

export default function MarketOverview({ data }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard icon={TrendingUp} label="Demand" value={score(data.demandScore)} helper="Local demand signal" />
      <MetricCard icon={Gauge} label="Opportunity" value={score(data.opportunityScore)} helper="Overall market opportunity" tone="accent" />
      <MetricCard icon={Users} label="Competition" value={score(data.competitionScore)} helper="Relative competitive pressure" />
      <MetricCard icon={IndianRupee} label="Market price" value={price(data.averageMarketPrice)} helper={data.averageMarketPrice == null ? 'No reliable local benchmark' : 'Average local benchmark'} />
    </div>
  )
}
