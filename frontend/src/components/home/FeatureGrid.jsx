import { Bot, LineChart, Landmark, Store } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

const items = [
  { icon: LineChart, titleKey: 'feature1Title', textKey: 'feature1Text' },
  { icon: Landmark, titleKey: 'feature2Title', textKey: 'feature2Text' },
  { icon: Bot, titleKey: 'feature3Title', textKey: 'feature3Text' },
  { icon: Store, titleKey: 'feature4Title', textKey: 'feature4Text' },
]

export default function FeatureGrid() {
  const { t } = useLanguage()

  return (
    <div className="page-container mt-6 pb-10">
      <div className="grid overflow-hidden rounded-2xl border border-white/80 bg-[#e4f0da] sm:grid-cols-2 lg:grid-cols-4">
        {items.map((item, index) => {
          const Icon = item.icon
          return (
            <div key={item.titleKey} className={`p-5 ${index < items.length - 1 ? 'lg:border-r lg:border-udyam-200/80' : ''} ${index % 2 === 0 ? 'sm:border-r sm:border-udyam-200/80 lg:border-r' : 'sm:border-r-0 lg:border-r'} ${index < 2 ? 'border-b border-udyam-200/80 lg:border-b-0' : 'lg:border-b-0'}`}>
              <Icon className="text-neutral-900" size={31} strokeWidth={1.7} />
              <div className="mt-3 text-sm font-semibold text-neutral-900">{t('homeExtra', item.titleKey)}</div>
              <div className="mt-1 text-xs leading-5 text-neutral-700">{t('homeExtra', item.textKey)}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
