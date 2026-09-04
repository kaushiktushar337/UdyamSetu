import { Headphones, Sparkles } from 'lucide-react'

export default function AssistantPanel() {
  return (
    <div className="soft-card p-5">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-full bg-udyam-50 text-udyam-700">
          <Sparkles size={19} />
        </div>
        <div>
          <div className="text-sm font-semibold text-neutral-900">UdyamSetu Assistant</div>
          <div className="text-[11px] text-emerald-600">● Online</div>
        </div>
      </div>

      <div className="mt-5 rounded-xl bg-[#f2f7ee] p-4 text-xs leading-5 text-neutral-600">
        I can explain schemes, calculate indicative loan structures, discuss market opportunities, and answer questions in simple language.
      </div>

      <button className="mt-5 ghost-button w-full">
        <Headphones size={16} /> Talk to Assistant
      </button>
    </div>
  )
}
