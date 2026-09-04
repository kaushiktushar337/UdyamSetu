export default function MetricCard({ label, value, helper, icon: Icon, tone = 'default' }) {
  const toneClass = tone === 'accent' ? 'text-udyam-700' : 'text-neutral-900'

  return (
    <div className="soft-card p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="text-[11px] font-medium uppercase tracking-wide text-neutral-500">{label}</div>
        {Icon && <div className="grid h-9 w-9 place-items-center rounded-xl bg-udyam-50 text-udyam-700"><Icon size={16} /></div>}
      </div>
      <div className={`mt-3 text-xl font-bold ${toneClass}`}>{value}</div>
      {helper && <div className="mt-1 text-[11px] text-neutral-500">{helper}</div>}
    </div>
  )
}
