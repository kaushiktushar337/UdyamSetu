export default function PageHeader({ title, subtitle, kicker }) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      {kicker && <div className="section-kicker">{kicker}</div>}
      <h1 className="mt-4 text-3xl font-bold tracking-tight text-neutral-950 sm:text-4xl">{title}</h1>
      <p className="mt-3 text-sm leading-6 text-neutral-600 sm:text-base">{subtitle}</p>
    </div>
  )
}
