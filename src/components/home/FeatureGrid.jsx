import { Bot, LineChart, Landmark, Store } from 'lucide-react'

const items = [
  { icon: LineChart, title: 'Hyper Local Market Analysis', text: 'Know what business works in your location' },
  { icon: Landmark, title: 'Smart Loan & Scheme Guide', text: 'Find the right scheme, amount and repayment plan' },
  { icon: Bot, title: 'AI Business Assistant', text: 'Get answers in your own language, anytime' },
  { icon: Store, title: 'Business Feasibility Report', text: 'Detailed strategy before you invest your money' },
]

export default function FeatureGrid() {
  return (
    <div className="page-container mt-6 pb-10">
      <div className="grid overflow-hidden rounded-2xl border border-white/80 bg-[#e4f0da] sm:grid-cols-2 lg:grid-cols-4">
        {items.map((item, index) => {
          const Icon = item.icon
          return (
            <div key={item.title} className={`p-5 ${index < items.length - 1 ? 'lg:border-r lg:border-udyam-200/80' : ''} ${index % 2 === 0 ? 'sm:border-r sm:border-udyam-200/80 lg:border-r' : 'sm:border-r-0 lg:border-r'} ${index < 2 ? 'border-b border-udyam-200/80 lg:border-b-0' : 'lg:border-b-0'}`}>
              <Icon className="text-neutral-900" size={31} strokeWidth={1.7} />
              <div className="mt-3 text-sm font-semibold text-neutral-900">{item.title}</div>
              <div className="mt-1 text-xs leading-5 text-neutral-700">{item.text}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
