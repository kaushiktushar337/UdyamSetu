import { LocateFixed, Loader2, MapPin } from 'lucide-react'
import { useState } from 'react'
import { requestCurrentLocation } from '../../utils/location'

export default function LocationButton({ onLocated, className = '' }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const locate = async () => {
    setLoading(true); setError('')
    try { const result = await requestCurrentLocation(); onLocated?.(result) }
    catch (err) { setError(err.message || 'Unable to detect location') }
    finally { setLoading(false) }
  }

  return (
    <div className={className}>
      <button type="button" onClick={locate} disabled={loading} className="ghost-button w-full px-4 py-2.5 text-xs disabled:opacity-60">
        {loading ? <Loader2 size={15} className="animate-spin" /> : <LocateFixed size={15} />}
        {loading ? 'Detecting location…' : 'Use my current location'}
      </button>
      {error && <div className="mt-2 flex items-start gap-1.5 text-[11px] leading-4 text-red-600"><MapPin size={13} className="mt-0.5 shrink-0" />{error}</div>}
    </div>
  )
}
