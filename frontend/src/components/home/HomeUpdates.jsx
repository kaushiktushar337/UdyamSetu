import { ArrowRight, CalendarDays, ExternalLink, Landmark, Newspaper } from 'lucide-react'
import { Link } from 'react-router-dom'
import { schemes } from '../../data/calculatorSchemes'
import { news } from '../../data/news'

const formatDate = (value) => new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(`${value}T00:00:00`))

export default function HomeUpdates() {
  return (
    <section className="page-container py-8 sm:py-10 font-sans">
      <div className="grid gap-7 lg:grid-cols-2">
        <article className="overflow-hidden rounded-[24px] border border-udyam-200 bg-white shadow-soft">
          <div className="bg-udyam-700 px-5 py-5 text-center sm:px-7">
            <div className="mx-auto flex w-fit items-center gap-2 text-white">
              <Newspaper size={21} strokeWidth={2} />
              <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">News &amp; Feeds</h2>
            </div>
          </div>
          <div className="h-[290px] overflow-y-auto bg-udyam-50 p-4 sm:h-[330px] sm:p-5">
            <div className="divide-y divide-udyam-200 overflow-hidden rounded-2xl border border-udyam-200 bg-white/70">
              {news.map((item) => (
                <div key={item.id} className="px-4 py-4 text-sm leading-6 text-neutral-900 sm:text-base">
                  <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] font-bold uppercase tracking-wide text-udyam-700"><span className="flex items-center gap-2"><CalendarDays size={13} /> {formatDate(item.date)}</span><span className="text-neutral-500">{item.category}</span></div>
                  <div className="font-semibold leading-5">{item.title}</div>
                  <p className="mt-1 text-xs leading-5 text-neutral-600 sm:text-sm">{item.summary}</p>
                  <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[10px] text-neutral-500"><span>{item.source}</span><a href={item.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-semibold text-udyam-700 hover:text-udyam-600">Official source <ExternalLink size={12} /></a></div>
                </div>
              ))}
            </div>
          </div>
        </article>

        <article className="overflow-hidden rounded-[24px] border border-udyam-200 bg-white shadow-soft">
          <div className="bg-udyam-700 px-5 py-5 text-center sm:px-7">
            <div className="mx-auto flex w-fit items-center gap-2 text-white">
              <Landmark size={21} strokeWidth={2} />
              <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">Loans &amp; Schemes</h2>
            </div>
          </div>
          <div className="h-[290px] overflow-y-auto bg-udyam-50 p-4 sm:h-[330px] sm:p-5">
            <div className="space-y-4 rounded-2xl border border-udyam-200 bg-white/70 p-4 text-sm leading-6 text-neutral-900 sm:text-base">
              <div>
                <div className="mb-1 text-[10px] font-bold uppercase tracking-wide text-udyam-700">Government schemes</div>
                <ul className="space-y-1">
                  {schemes.map((scheme) => (
                    <li key={scheme.id} className="flex gap-3 py-2">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-udyam-600" aria-hidden="true" />
                      <span><strong>{scheme.name}</strong>: {scheme.summary}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="border-t border-udyam-200 pt-3">
                <div className="mb-1 text-[10px] font-bold uppercase tracking-wide text-udyam-700">Loan routes</div>
                <ul className="space-y-1">
                  {schemes.map((scheme) => (
                    <li key={`${scheme.id}-loan`} className="flex gap-3 py-2">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-udyam-600" aria-hidden="true" />
                      <span><strong>{scheme.name} loan</strong>: {scheme.loan} at {scheme.interest}, up to {scheme.tenure}.</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex gap-3 border-t border-udyam-200 pt-3">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-udyam-600" aria-hidden="true" />
                <span>Check your indicative eligibility with the Smart Calculator.</span>
              </div>
            </div>
            <Link to="/schemes" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-udyam-700 hover:text-udyam-600">
              View all scheme details <ArrowRight size={15} />
            </Link>
          </div>
        </article>
      </div>
    </section>
  )
}
