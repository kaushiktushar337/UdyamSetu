import { Gauge } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

export default function CompetitionSnapshot({ data }) {
  const { t } = useLanguage()
  return (
    <div className="soft-card p-5">
      <div className="flex items-center justify-between gap-4">
        <div className="text-sm font-semibold text-neutral-900">{t('insights', 'competition')}</div>
        <Gauge size={17} className="text-udyam-700" />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-neutral-50 p-3">
          <div className="text-[10px] text-neutral-500">{t('insights', 'existing')} {data.category.toLowerCase()}</div>
          <div className="mt-1 text-lg font-bold">{data.existingBusinesses}</div>
        </div>
        <div className="rounded-xl bg-neutral-50 p-3">
          <div className="text-[10px] text-neutral-500">{t('insights', 'level')}</div>
          <div className="mt-1 text-sm font-semibold text-amber-600">Medium</div>
        </div>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between text-[11px] text-neutral-500">
          <span>{t('insights', 'saturation')}</span>
          <span className="font-semibold text-neutral-800">{data.saturation}%</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-neutral-100">
          <div className="h-full rounded-full bg-udyam-500" style={{ width: `${data.saturation}%` }} />
        </div>
      </div>
    </div>
  )
}
