export default function ProgressBar({ value, label, helper }) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-neutral-600">{label}</span>
        <span className="font-semibold text-neutral-900">{value}%</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-neutral-100">
        <div className="h-full rounded-full bg-udyam-500" style={{ width: `${value}%` }} />
      </div>
      {helper && <div className="mt-1 text-[11px] text-neutral-500">{helper}</div>}
    </div>
  )
}
