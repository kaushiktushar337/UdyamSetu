import FormattedMessage from './FormattedMessage'
import { useEffect, useRef } from 'react'

export default function ChatWindow({ messages, loading = false }) {
  const endRef = useRef(null)
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }) }, [messages, loading])
  return (
    <div className="grid max-h-[520px] gap-4 overflow-y-auto pr-1">
      {messages.map((message, index) => (
        <div key={`${message.role}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`max-w-[88%] rounded-2xl px-4 py-3 text-xs leading-5 sm:max-w-[75%] ${message.role === 'user' ? 'rounded-br-md bg-[#dceccf] text-neutral-800' : 'rounded-bl-md border border-neutral-100 bg-white text-neutral-700 shadow-sm'}`}>
            {message.role === 'assistant' ? <FormattedMessage content={message.content} /> : <span className="whitespace-pre-wrap">{message.content}</span>}
          </div>
        </div>
      ))}
      {loading && <div className="flex justify-start"><div className="rounded-2xl rounded-bl-md border border-neutral-100 bg-white px-4 py-3 shadow-sm"><span className="inline-flex items-center gap-1 text-xs text-neutral-500"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neutral-400" /><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neutral-400 [animation-delay:120ms]" /><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neutral-400 [animation-delay:240ms]" /></span></div></div>}
      <div ref={endRef} aria-hidden="true" />
    </div>
  )
}
