import MetricCard from '../common/MetricCard'
import { IndianRupee, Landmark, Percent, Calculator } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

function formatINR(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(value)
}

export default function FinancialResults({ result }) {
  const { t } = useLanguage()

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <MetricCard icon={Calculator} label={t('calculator', 'theoretical')} value={`₹${formatINR(result.theoreticalProjectCost)}`} helper={t('calculator', 'theoreticalHelp')} />
      <MetricCard icon={Landmark} label={t('calculator', 'eligible')} value={`₹${formatINR(result.eligibleProjectCost)}`} helper={result.capped ? t('calculator', 'eligibleCapped') : t('calculator', 'eligibleWithin')} tone="accent" />
      <MetricCard icon={IndianRupee} label={t('calculator', 'maxLoan')} value={`₹${formatINR(result.loanAmount)}`} helper={`${result.loanPercent}% of eligible cost`} />
      <MetricCard icon={IndianRupee} label={t('calculator', 'own')} value={`₹${formatINR(result.requiredMargin)}`} helper={result.additionalMargin > 0 ? `₹${formatINR(result.additionalMargin)} ${t('calculator', 'additional')}` : t('calculator', 'sufficient')} />
      <MetricCard icon={Percent} label={t('calculator', 'recommended')} value={result.scheme.name.replace(' Scheme', '')} helper={`${result.scheme.interest} p.a.`} tone="accent" />
    </div>
  )
}
