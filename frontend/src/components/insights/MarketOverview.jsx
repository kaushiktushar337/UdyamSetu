import { Gauge, TrendingUp, IndianRupee, Users } from 'lucide-react'
import MetricCard from '../common/MetricCard'

function value(value, suffix = '') {
  return value == null ? '—' : `${Number(value).toFixed(0)}${suffix}`
}

export default function MarketOverview({ data }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard icon={TrendingUp} label="Demand" value={value(data.demandScore, '/100')} helper="Local market signal" />
      <MetricCard icon={Gauge} label="Opportunity" value={value(data.opportunityScore, '/100')} helper="Combined market signal" tone="accent" />
      <MetricCard icon={Users} label="Competition" value={value(data.competitionScore, '/100')} helper={`${data.competitionCount == null ? '—' : Number(data.competitionCount).toLocaleString('en-IN')} estimated businesses`} />
      <MetricCard icon={IndianRupee} label="Market price" value={data.averageMarketPrice == null ? '—' : `₹${Number(data.averageMarketPrice).toLocaleString('en-IN')}`} helper={data.averageMarketPrice == null ? 'No reliable local benchmark' : 'Local benchmark'} />
    </div>
  )
}
