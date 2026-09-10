const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 90000)

function messageFromDetail(detail) {
  if (!detail) return null
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || item?.message || String(item)).filter(Boolean).join(' • ')
  }
  if (typeof detail === 'object') return detail.message || detail.error || detail.detail || null
  return String(detail)
}

export function friendlyError(error, fallback = 'Something went wrong. Please try again.') {
  if (error instanceof Error && error.message && error.message !== '[object Object]') return error.message
  return fallback
}

async function request(path, options = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: options.signal || controller.signal,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...(options.headers || {}) },
    })

    const contentType = response.headers.get('content-type') || ''
    const data = contentType.includes('application/json') ? await response.json().catch(() => ({})) : await response.text()

    if (!response.ok) {
      const detail = typeof data === 'object' ? messageFromDetail(data.detail) || messageFromDetail(data) : data
      throw new Error(detail || `Request failed (${response.status})`)
    }
    return data
  } catch (error) {
    if (error?.name === 'AbortError') throw new Error('The request took too long. Please try again.')
    if (error instanceof TypeError) throw new Error('Unable to reach UdyamSetu. Please make sure the backend is running.')
    throw error
  } finally {
    clearTimeout(timeout)
  }
}

export function getUserId() {
  const key = 'udyamsetu-user-id'
  let id = window.localStorage.getItem(key)
  if (!id) {
    id = window.crypto?.randomUUID?.() || `browser-${Date.now()}-${Math.random().toString(36).slice(2)}`
    window.localStorage.setItem(key, id)
  }
  return id
}

export function chat(message, conversationId = null, userId = getUserId(), locationText = null) {
  return request('/api/chat', { method: 'POST', body: JSON.stringify({ message, conversation_id: conversationId, user_id: userId, location_text: locationText }) })
}

export function getChatHistory(conversationId) {
  return request(`/api/chat/history/${encodeURIComponent(conversationId)}`)
}

export function saveUserLocation(payload) {
  return request('/api/location', { method: 'POST', body: JSON.stringify(payload) })
}

export function getLatestUserLocation(userId = getUserId()) {
  return request(`/api/location/latest/${encodeURIComponent(userId)}`)
}

export function getLocations() {
  return request('/api/locations')
}

export function getInsights(payload) {
  return request('/api/insights', { method: 'POST', body: JSON.stringify(payload) })
}

export function getFundingRecommendations(payload) {
  return request('/api/funding/recommendations', { method: 'POST', body: JSON.stringify(payload) })
}

export function analyzeBusiness(payload) {
  return request('/api/analyze', { method: 'POST', body: JSON.stringify(payload) })
}

export function healthCheck() {
  return request('/health')
}
