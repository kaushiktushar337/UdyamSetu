export default function StatCard({ icon: Icon, value, label, tone = 'green' }) {
  const styles = tone === 'green'
    ? 'bg-udyam-50 text-udyam-700'
    : 'bg-neutral-50 text-neutral-700'

  return (
    <div className="flex items-center gap-3">
      <div className={`grid h-9 w-9 place-items-center rounded-xl ${styles}`}>
        {Icon ? <Icon size={18} /> : null}
      </div>
      <div>
        <div className="text-sm font-bold text-neutral-900">{value}</div>
        <div className="text-[11px] text-neutral-500">{label}</div>
      </div>
    </div>
  )
}
