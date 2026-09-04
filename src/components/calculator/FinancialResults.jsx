import MetricCard from '../common/MetricCard'
import { IndianRupee, Landmark, Percent, Calculator } from 'lucide-react'

function formatINR(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(value)
}

export default function FinancialResults({ result }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <MetricCard icon={Calculator} label="Theoretical Project Cost" value={`₹${formatINR(result.theoreticalProjectCost)}`} helper="Based on 10% margin" />
      <MetricCard icon={Landmark} label="Maximum Loan Amount" value={`₹${formatINR(result.loanAmount)}`} helper={`${result.loanPercent}% of project cost`} tone="accent" />
      <MetricCard icon={IndianRupee} label="Your Margin (10%)" value={`₹${formatINR(result.requiredMargin)}`} />
      <MetricCard icon={Percent} label="Recommended Scheme" value={result.scheme.name.replace(' Scheme', '')} helper={`${result.scheme.interest} p.a.`} tone="accent" />
    </div>
  )
}
