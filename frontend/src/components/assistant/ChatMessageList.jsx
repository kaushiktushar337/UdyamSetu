import ChatWindow from './ChatWindow'

export default function ChatMessageList({ messages }) {
  return (
    <div className="min-h-[410px] rounded-2xl border border-neutral-100 bg-[#fbfcfa] p-4 sm:p-5">
      <ChatWindow messages={messages} />
    </div>
  )
}
