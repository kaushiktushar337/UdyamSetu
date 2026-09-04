import { ArrowUp } from 'lucide-react'
import { useState } from 'react'

export default function ChatInput({ onSend }) {
  const [value, setValue] = useState('')

  const submit = (event) => {
    event.preventDefault()
    const text = value.trim()
    if (!text) return
    onSend(text)
    setValue('')
  }

  return (
    <form onSubmit={submit} className="flex overflow-hidden rounded-xl border border-neutral-200 bg-white">
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Type your message..."
        className="min-w-0 flex-1 px-4 py-3 text-xs outline-none"
      />
      <button className="grid w-12 place-items-center bg-udyam-600 text-white">
        <ArrowUp size={16} />
      </button>
    </form>
  )
}
