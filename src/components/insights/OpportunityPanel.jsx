import { CheckCircle2 } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

export default function OpportunityPanel({ data }) {
  const { t } = useLanguage()

  return (
    <div className="soft-card p-5">
      <div className="text-sm font-semibold text-neutral-900">{t('insights', 'opportunity')}</div>
      <p className="mt-2 text-xs leading-5 text-neutral-600">{data.demand} demand signal for {data.category.toLowerCase()} in the selected area. These opportunities are model suggestions, not guaranteed demand.</p>

      <div className="mt-4 inline-flex rounded-full bg-udyam-50 px-3 py-1 text-[10px] font-semibold text-udyam-700">
        Top Opportunities
      </div>

      <div className="mt-4 grid gap-3">
        {data.topOpportunities.map((item) => (
          <div key={item} className="flex items-center gap-2 text-xs text-neutral-700">
            <CheckCircle2 size={15} className="text-udyam-600" />
            {item}
          </div>
        ))}
      </div>
    </div>
  )
}
