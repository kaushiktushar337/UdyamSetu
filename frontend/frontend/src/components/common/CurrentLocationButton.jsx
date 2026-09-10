import { MapPin, LoaderCircle } from 'lucide-react'
import { useState } from 'react'
import { getUserId, saveUserLocation, friendlyError } from '../../services/api'

export default function CurrentLocationButton({ onResolved, className = '' }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const locate = () => {
    setError('')
    if (!navigator.geolocation) {
      setError('Location is not available in this browser.')
      return
    }

    setLoading(true)
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const result = await saveUserLocation({ user_id: getUserId(), latitude: coords.latitude, longitude: coords.longitude, accuracy: coords.accuracy })
          onResolved?.(result)
        } catch (requestError) {
          setError(friendlyError(requestError, 'We could not save your location. Please try again.'))
        } finally {
          setLoading(false)
        }
      },
      (geoError) => {
        const messages = {
          1: 'Location permission was not granted.',
          2: 'We could not determine your location. Please try again.',
          3: 'Location lookup took too long. Please try again.',
        }
        setError(messages[geoError.code] || 'We could not determine your location.')
        setLoading(false)
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 },
    )
  }

  return (
    <div className={className}>
      <button type="button" onClick={locate} disabled={loading} className="ghost-button w-full justify-center disabled:cursor-not-allowed disabled:opacity-60">
        {loading ? <LoaderCircle size={16} className="animate-spin" /> : <MapPin size={16} />}
        {loading ? 'Finding your location…' : 'Use my current location'}
      </button>
      {error && <p role="alert" className="mt-2 text-[11px] leading-4 text-red-600">{error}</p>}
    </div>
  )
}
