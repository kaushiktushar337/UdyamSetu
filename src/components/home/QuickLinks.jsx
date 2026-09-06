import { ArrowRight, BarChart3, Calculator, MessageCircle, Landmark } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useLanguage } from '../../context/LanguageContext'

const links = [
  { icon: BarChart3, titleKey: 'insightsTitle', textKey: 'insightsText', to: '/insights' },
  { icon: Calculator, titleKey: 'calculatorTitle', textKey: 'calculatorText', to: '/calculator' },
  { icon: MessageCircle, titleKey: 'assistantTitle', textKey: 'assistantText', to: '/assistant' },
  { icon: Landmark, titleKey: 'schemesTitle', textKey: 'schemesText', to: '/schemes' },
]

export default function QuickLinks() {
  const { t } = useLanguage()

  return (
    <section className="page-container pb-12">
      <div className="mb-4 text-sm font-semibold text-neutral-800">{t('home', 'explore')}</div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {links.map((link) => {
          const Icon = link.icon
          return (
            <Link key={link.to} to={link.to} className="soft-card group p-5 transition hover:-translate-y-0.5 hover:shadow-soft">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-udyam-50 text-udyam-700">
                <Icon size={19} />
              </div>
              <div className="mt-4 text-sm font-semibold text-neutral-900">{t('home', link.titleKey)}</div>
              <div className="mt-1 text-xs leading-5 text-neutral-500">{t('home', link.textKey)}</div>
              <div className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-udyam-700">
                {t('home', 'exploreAction')} <ArrowRight size={13} />
              </div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
