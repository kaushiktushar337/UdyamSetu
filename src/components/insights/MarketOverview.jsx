import { Users, Home, Wallet, Sparkles } from 'lucide-react'
import MetricCard from '../common/MetricCard'
import { useLanguage } from '../../context/LanguageContext'

export default function MarketOverview({ data }) {
  const { t } = useLanguage()

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard icon={Users} label={t('insights', 'population')} value={data.population.toLocaleString('en-IN')} />
      <MetricCard icon={Home} label={t('insights', 'households')} value={data.households.toLocaleString('en-IN')} />
      <MetricCard icon={Wallet} label={t('insights', 'income')} value={`₹${data.avgMonthlyIncome.toLocaleString('en-IN')}`} />
      <MetricCard icon={Sparkles} label={t('insights', 'potential')} value={data.potential} tone="accent" helper={t('insights', 'estimate')} />
    </div>
  )
}
