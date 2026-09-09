import { ArrowRight, Landmark, Newspaper } from 'lucide-react'
import { Link } from 'react-router-dom'
import { schemes } from '../../data/schemes'

const updates = [
  'Explore practical business opportunities connected to local agriculture and rural demand.',
  'Compare project costs, loan eligibility, and repayment structures before you apply.',
  'Use the Business Insights view to understand demand and competition in your area.',
]

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
              {updates.map((update) => (
                <div key={update} className="px-4 py-4 text-sm leading-6 text-neutral-900 sm:text-base">
                  {update}
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
            <ul className="space-y-1 rounded-2xl border border-udyam-200 bg-white/70 p-4 text-sm leading-6 text-neutral-900 sm:text-base">
              {schemes.map((scheme) => (
                <li key={scheme.id} className="flex gap-3 py-2">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-udyam-600" aria-hidden="true" />
                  <span>{scheme.name}: {scheme.summary}</span>
                </li>
              ))}
              <li className="flex gap-3 py-2">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-udyam-600" aria-hidden="true" />
                <span>Check your indicative eligibility with the Smart Calculator.</span>
              </li>
            </ul>
            <Link to="/schemes" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-udyam-700 hover:text-udyam-600">
              View all scheme details <ArrowRight size={15} />
            </Link>
          </div>
        </article>
      </div>
    </section>
  )
}
