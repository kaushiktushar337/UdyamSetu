import { useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import PageHeader from '../components/common/PageHeader'
import SchemeTabs from '../components/schemes/SchemeTabs'
import SchemeCard from '../components/schemes/SchemeCard'
import SchemeNotice from '../components/schemes/SchemeNotice'
import { schemes } from '../data/schemes'

export default function Schemes() {
  const [active, setActive] = useState('micro')
  const current = schemes.find((scheme) => scheme.id === active)

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        title="Government Schemes for You"
        subtitle="We match your project with the best suitable financing structure."
      />

      <div className="mt-8 text-center">
        <SchemeTabs active={active} onChange={setActive} schemes={schemes} />
      </div>

      <div className="mx-auto mt-5 max-w-5xl">
        <SchemeCard scheme={current} />
      </div>

      <div className="mx-auto mt-5 max-w-5xl">
        <SchemeNotice />
      </div>

      <div className="mx-auto mt-5 max-w-5xl rounded-2xl border border-neutral-100 bg-white/70 p-5">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <div className="text-sm font-semibold text-neutral-900">Want to know which scheme fits your project?</div>
            <div className="mt-1 text-xs text-neutral-500">Use the calculator to route your indicative project cost automatically.</div>
          </div>
          <Link to="/calculator" className="green-button">
            Try Calculator <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  )
}
