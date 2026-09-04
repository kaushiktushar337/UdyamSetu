export default function SectionCard({ title, subtitle, children, action }) {
  return (
    <section className="soft-card p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-neutral-900">{title}</h2>
          {subtitle && <p className="mt-1 text-xs leading-5 text-neutral-500">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className="mt-5">{children}</div>
    </section>
  )
}
