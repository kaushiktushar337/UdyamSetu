import { ArrowRight, CircleUserRound, Leaf, LineChart, WalletCards } from 'lucide-react'

const steps = [
  {
    icon: CircleUserRound,
    title: 'Share Your Details',
    text: 'Tell us your location, available margin money and business idea.',
  },
  {
    icon: LineChart,
    title: 'Get Local Insights',
    text: 'Our AI analyzes market demand, competition and opportunities in your area.',
  },
  {
    icon: WalletCards,
    title: 'See Financial Plan',
    text: 'Know total project cost, loan eligibility, EMI and scheme details instantly.',
  },
  {
    icon: Leaf,
    title: 'Start with Confidence',
    text: 'Take an informed decision and build a profitable, sustainable business.',
  },
]

export default function ProcessSteps() {
  return (
    <div className="grid gap-3 md:grid-cols-4">
      {steps.map((step, index) => {
        const Icon = step.icon
        return (
          <div key={step.title} className="relative">
            <div className="soft-card h-full p-5">
              <div className="mx-auto grid h-11 w-11 place-items-center rounded-full bg-udyam-50 text-udyam-700">
                <Icon size={21} />
              </div>
              <div className="mt-4 text-center text-sm font-semibold text-neutral-900">{step.title}</div>
              <div className="mt-2 text-center text-xs leading-5 text-neutral-500">{step.text}</div>
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
