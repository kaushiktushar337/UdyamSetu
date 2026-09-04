export default function ChatWindow({ messages }) {
  return (
    <div className="grid gap-4">
      {messages.map((message, index) => (
        <div key={`${message.role}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div
            className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-5 sm:max-w-[72%] ${
              message.role === 'user'
                ? 'rounded-br-md bg-[#dceccf] text-neutral-800'
                : 'rounded-bl-md border border-neutral-100 bg-white text-neutral-700 shadow-sm'
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}
    </div>
  )
}
