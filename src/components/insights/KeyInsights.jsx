import { CheckCircle2 } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

const bullets = [
  'Dairy business has good potential in your area.',
  'Focus on quality and doorstep delivery to stand out.',
  'Value added products can give higher returns.',
]

export default function KeyInsights() {
  const { t } = useLanguage()

  return (
    <div className="soft-card p-5">
      <div className="text-sm font-semibold text-neutral-900">{t('insights', 'key')}</div>
      <div className="mt-4 grid gap-3">
        {bullets.map((bullet) => (
          <div key={bullet} className="flex gap-2 text-xs leading-5 text-neutral-700">
            <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-udyam-600" />
            {bullet}
          </div>
        ))}
      </div>
      <div className="mt-4 text-[10px] text-neutral-500">{t('insights', 'prototype')}</div>
    </div>
  )
}
