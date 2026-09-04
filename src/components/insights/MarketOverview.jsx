import { Users, Home, Wallet, Sparkles } from 'lucide-react'
import MetricCard from '../common/MetricCard'

export default function MarketOverview() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard icon={Users} label="Population (10km radius)" value="25,420" />
      <MetricCard icon={Home} label="Estimated Households" value="4,240" />
      <MetricCard icon={Wallet} label="Avg. Monthly Income" value="₹9,850" />
      <MetricCard icon={Sparkles} label="Market Potential" value="High" tone="accent" helper="Model estimate" />
    </div>
  )
}
