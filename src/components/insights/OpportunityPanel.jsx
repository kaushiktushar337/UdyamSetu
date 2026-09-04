import { CheckCircle2 } from 'lucide-react'

const items = ['Packaged Milk', 'Paneer & Curd', 'Ghee & Butter', 'Flavoured Milk']

export default function OpportunityPanel() {
  return (
    <div className="soft-card p-5">
      <div className="text-sm font-semibold text-neutral-900">Demand & Opportunity</div>
      <p className="mt-2 text-xs leading-5 text-neutral-600">High demand for milk, paneer and curd in your area. Scope for value-added dairy products.</p>

      <div className="mt-4 inline-flex rounded-full bg-udyam-50 px-3 py-1 text-[10px] font-semibold text-udyam-700">
        Top Opportunities
      </div>

      <div className="mt-4 grid gap-3">
        {items.map((item) => (
          <div key={item} className="flex items-center gap-2 text-xs text-neutral-700">
            <CheckCircle2 size={15} className="text-udyam-600" />
            {item}
          </div>
        ))}
      </div>
    </div>
  )
}
