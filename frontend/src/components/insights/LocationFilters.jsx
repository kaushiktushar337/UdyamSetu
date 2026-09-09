import { useEffect, useMemo, useState } from 'react'
import { LoaderCircle } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'
import { getLocations, friendlyError } from '../../services/api'
import CurrentLocationButton from '../common/CurrentLocationButton'

const fallback = { state: 'Uttar Pradesh', district: 'Prayagraj', block: 'Soraon', category: 'Dairy', locationId: null, locationText: '' }
const categories = ['Dairy', 'Retail', 'Food Processing', 'Textiles', 'Services', 'Agriculture-linked activity']

function labelFor(location) {
  return [location.location_name, location.district, location.state].filter(Boolean).join(', ')
}

export default function LocationFilters({ onApply }) {
  const { t } = useLanguage()
  const [filters, setFilters] = useState(fallback)
  const [locations, setLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getLocations()
      .then((data) => {
        const list = Array.isArray(data?.locations) ? data.locations : []
        setLocations(list)
        const preferred = list.find((x) => /prayagraj/i.test(labelFor(x))) || list[0]
        if (preferred) {
          setFilters((current) => ({ ...current, state: preferred.state || current.state, district: preferred.district || current.district, block: preferred.location_name || current.block, locationId: preferred.location_id, locationText: labelFor(preferred) }))
        }
      })
      .catch((requestError) => setError(friendlyError(requestError, 'Could not load supported locations.')))
      .finally(() => setLoading(false))
  }, [])

  const locationOptions = useMemo(() => locations.map((location) => ({ ...location, label: labelFor(location) })).filter((x) => x.label), [locations])

  const selectLocation = (event) => {
    const location = locationOptions.find((x) => String(x.location_id) === event.target.value)
    if (!location) return
    setFilters((current) => ({ ...current, state: location.state || '', district: location.district || '', block: location.location_name || '', locationId: location.location_id, locationText: location.label }))
  }

  const apply = () => onApply(filters)

  return (
    <div className="soft-card p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-neutral-900">Location & business</div>
          <p className="mt-1 text-xs text-neutral-500">Choose an area or use your current location.</p>
        </div>
        <CurrentLocationButton onResolved={(result) => {
          if (result?.location_id || result?.estimated_address) {
            setFilters((current) => ({ ...current, locationId: result.location_id || current.locationId, locationText: result.estimated_address || current.locationText, block: result.estimated_address || current.block }))
            onApply({ ...filters, locationId: result.location_id || filters.locationId, locationText: result.estimated_address || filters.locationText, block: result.estimated_address || filters.block })
          }
        }} className="sm:w-auto" />
      </div>

      {loading ? (
        <div className="mt-5 flex items-center gap-2 text-xs text-neutral-500"><LoaderCircle size={14} className="animate-spin" /> Loading supported locations…</div>
      ) : (
        <div className="mt-5 grid gap-3 md:grid-cols-[1fr_1fr_1.35fr]">
          <label className="grid gap-1.5">
            <span className="text-[11px] font-medium text-neutral-500">Location</span>
            <select value={filters.locationId || ''} onChange={selectLocation} className="h-10 rounded-xl border border-neutral-200 bg-white px-3 text-xs outline-none focus:border-udyam-400">
              {!locationOptions.length && <option value="">No locations available</option>}
              {locationOptions.map((location) => <option key={location.location_id} value={location.location_id}>{location.label}</option>)}
            </select>
          </label>
          <label className="grid gap-1.5">
            <span className="text-[11px] font-medium text-neutral-500">{t('insights', 'category')}</span>
            <select value={filters.category} onChange={(event) => setFilters((current) => ({ ...current, category: event.target.value }))} className="h-10 rounded-xl border border-neutral-200 bg-white px-3 text-xs outline-none focus:border-udyam-400">
              {categories.map((category) => <option key={category}>{category}</option>)}
            </select>
          </label>
          <button onClick={apply} disabled={!filters.locationId} className="green-button self-end disabled:cursor-not-allowed disabled:opacity-50">{t('insights', 'get')}</button>
        </div>
      )}

      {filters.locationText && <div className="mt-3 text-xs text-neutral-600">Selected area: <span className="font-semibold text-neutral-900">{filters.locationText}</span></div>}
      {error && <div role="alert" className="mt-3 rounded-xl bg-red-50 p-3 text-xs text-red-700">{error}</div>}
    </div>
  )
}
