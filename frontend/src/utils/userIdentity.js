const KEY = 'udyamsetu-local-user-id'
export function getLocalUserId() {
  let id = window.localStorage.getItem(KEY)
  if (!id) {
    id = window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`
    window.localStorage.setItem(KEY, id)
  }
  return id
}
