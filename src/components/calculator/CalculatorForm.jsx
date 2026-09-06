import { useState } from 'react'
import { useLanguage } from '../../context/LanguageContext'

export default function CalculatorForm({ onCalculate, initial }) {
  const { t } = useLanguage()
  const [form, setForm] = useState(initial)

  const update = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }))

  return (
    <div className="soft-card p-5">
      <div className="text-sm font-semibold text-neutral-900">{t('calculator', 'details')}</div>
      <div className="mt-5 grid gap-4">
        <label className="grid gap-1.5">
          <span className="text-[11px] font-medium text-neutral-600">{t('calculator', 'margin')}</span>
          <input
            type="number"
            value={form.margin}
            onChange={update('margin')}
            className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400"
          />
        </label>

        <label className="grid gap-1.5">
          <span className="text-[11px] font-medium text-neutral-600">{t('calculator', 'category')}</span>
          <select value={form.category} onChange={update('category')} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400">
            <option>Dairy</option>
            <option>Retail</option>
            <option>Food Processing</option>
            <option>Textiles</option>
            <option>Services</option>
          </select>
        </label>

        <label className="grid gap-1.5">
          <span className="text-[11px] font-medium text-neutral-600">{t('calculator', 'location')}</span>
          <input
            value={form.location}
            onChange={update('location')}
            className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400"
          />
        </label>

        <button onClick={() => onCalculate(form)} className="green-button mt-1 w-full">
          {t('calculator', 'calculate')}
        </button>
      </div>
    </div>
  )
}
