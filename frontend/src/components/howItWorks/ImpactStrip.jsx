import { Users, Store, MapPin, Star } from 'lucide-react'
import StatCard from '../common/StatCard'
import { useLanguage } from '../../context/LanguageContext'

export default function ImpactStrip() {
  const { t } = useLanguage()

  return (
    <div className="rounded-2xl border border-udyam-100 bg-[#edf5e7] p-6 sm:p-8">
      <div className="text-center text-base font-semibold text-udyam-800">{t('how', 'impact')}</div>
      <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} value="10L+" label={t('how', 'rural')} />
        <StatCard icon={Store} value="500+" label={t('how', 'categories')} />
        <StatCard icon={MapPin} value="5L+" label={t('how', 'villages')} />
        <StatCard icon={Star} value="95%" label={t('how', 'satisfaction')} />
      </div>
    </div>
  )
}
