import { saveUserLocation } from '../services/api'
import { getLocalUserId } from './userIdentity'

export function requestCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Live location is not supported by this browser.'))
      return
    }
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const result = await saveUserLocation({
            user_id: getLocalUserId(),
            latitude: coords.latitude,
            longitude: coords.longitude,
            accuracy: coords.accuracy,
          })
          resolve(result)
        } catch (error) { reject(error) }
      },
      (error) => reject(new Error(error.code === 1 ? 'Location permission was denied.' : 'Could not detect your current location.')),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 },
    )
  })
}
