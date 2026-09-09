import { ArrowRight, CircleUserRound, Leaf, LineChart, WalletCards } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

const steps = [
  {
    icon: CircleUserRound,
    titleKey: 'step1Title',
    textKey: 'step1Text',
  },
  {
    icon: LineChart,
    titleKey: 'step2Title',
    textKey: 'step2Text',
  },
  {
    icon: WalletCards,
    titleKey: 'step3Title',
    textKey: 'step3Text',
  },
  {
    icon: Leaf,
    titleKey: 'step4Title',
    textKey: 'step4Text',
  },
]

export default function ProcessSteps() {
  const { t } = useLanguage()

  return (
    <div className="grid gap-3 md:grid-cols-4">
      {steps.map((step, index) => {
        const Icon = step.icon
        return (
          <div key={step.titleKey} className="relative">
            <div className="soft-card h-full p-5">
              <div className="mx-auto grid h-11 w-11 place-items-center rounded-full bg-udyam-50 text-udyam-700">
                <Icon size={21} />
              </div>
              <div className="mt-4 text-center text-sm font-semibold text-neutral-900">{t('how', step.titleKey)}</div>
              <div className="mt-2 text-center text-xs leading-5 text-neutral-500">{t('how', step.textKey)}</div>
            </div>
            {index < steps.length - 1 && (
              <div className="absolute right-[-12px] top-1/2 hidden -translate-y-1/2 text-udyam-600 md:block">
                <ArrowRight size={18} />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
