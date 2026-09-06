import { useState } from 'react'
import { useLanguage } from '../../context/LanguageContext'

const defaults = {
  state: 'Uttar Pradesh',
  district: 'Prayagraj',
  block: 'Soraon',
  category: 'Dairy',
}

const options = {
  state: ['Uttar Pradesh', 'Other'],
  district: ['Prayagraj', 'Other'],
  block: ['Soraon', 'Other'],
  category: ['Dairy', 'Retail', 'Food Processing', 'Textiles', 'Services'],
}

export default function LocationFilters({ onApply }) {
  const { t } = useLanguage()
  const [filters, setFilters] = useState(defaults)

  const update = (key) => (event) => setFilters((current) => ({ ...current, [key]: event.target.value }))

  return (
    <div className="soft-card p-4">
      <div className="grid gap-3 md:grid-cols-4">
        {Object.entries(filters).map(([key, value]) => (
          <label key={key} className="grid gap-1.5">
            <span className="text-[11px] font-medium capitalize text-neutral-500">{t('insights', key)}</span>
            <select
              value={value}
              onChange={update(key)}
              className="h-10 rounded-xl border border-neutral-200 bg-white px-3 text-xs outline-none focus:border-udyam-400"
            >
              {options[key].map((option) => <option key={option}>{option}</option>)}
            </select>
          </label>
        ))}
        <button onClick={() => onApply(filters)} className="green-button self-end">
          {t('insights', 'get')}
        </button>
      </div>
    </div>
  )
}
