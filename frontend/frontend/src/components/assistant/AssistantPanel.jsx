import { Headphones, Sparkles } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

export default function AssistantPanel() {
  const { t } = useLanguage()

  return (
    <div className="soft-card p-5">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-full bg-udyam-50 text-udyam-700">
          <Sparkles size={19} />
        </div>
        <div>
          <div className="text-sm font-semibold text-neutral-900">{t('assistant', 'name')}</div>
          <div className="text-[11px] text-emerald-600">● {t('assistant', 'online')}</div>
        </div>
      </div>

      <div className="mt-5 rounded-xl bg-[#f2f7ee] p-4 text-xs leading-5 text-neutral-600">
        {t('assistant', 'description')}
      </div>

      <button className="mt-5 ghost-button w-full">
        <Headphones size={16} /> {t('assistant', 'talk')}
      </button>
    </div>
  )
}
