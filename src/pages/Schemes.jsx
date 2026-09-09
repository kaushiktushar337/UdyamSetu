import { useMemo, useState } from 'react'
import { ArrowRight, Landmark, Search, Target, ExternalLink } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import SchemeCard from '../components/schemes/SchemeCard'
import SchemeNotice from '../components/schemes/SchemeNotice'
import { businessCategories } from '../data/businessCategories'
import { useLanguage } from '../context/LanguageContext'
import { getRecommendations, getDecision } from '../utils/engine'

const initialProfile = {
  category: 'Dairy',
  projectCost: '',
  monthlyIncome: '',
  loanAmount: '',
}

export default function Schemes() {
  const { t } = useLanguage()
  const [mode, setMode] = useState('scheme')
  const [profile, setProfile] = useState(initialProfile)

  const decision = useMemo(() => getDecision(profile, mode), [profile, mode])
  const recommendations = decision.recommendations
  const bestFit = decision.bestFit

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        title={t('schemes', 'title')}
        subtitle={t('schemes', 'subtitle')}
      />

      <div className="mt-8 grid gap-8 xl:grid-cols-[420px_minmax(420px,1fr)]">
        <section className="soft-card rounded-[28px] border border-udyam-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-udyam-700">
                <Target size={16} /> Assessment
              </div>
              <div className="mt-2 text-2xl font-bold tracking-tight text-neutral-950">Find your fit</div>
            </div>
            <div className="rounded-2xl bg-udyam-50 p-2 text-udyam-700">
              <Search size={20} />
            </div>
          </div>

          <div className="mt-5 flex rounded-2xl border border-udyam-200 bg-udyam-50 p-1">
            <button
              type="button"
              onClick={() => setMode('scheme')}
              className={`flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition ${mode === 'scheme' ? 'bg-udyam-700 text-white shadow-soft' : 'text-udyam-700 hover:bg-white'}`}
            >
              Schemes
            </button>
            <button
              type="button"
              onClick={() => setMode('loanPlan')}
              className={`flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition ${mode === 'loanPlan' ? 'bg-udyam-700 text-white shadow-soft' : 'text-udyam-700 hover:bg-white'}`}
            >
              Loan Plans
            </button>
          </div>

          <div className="mt-6 space-y-4">
            <label className="grid gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Business category</span>
              <select
                value={profile.category}
                onChange={(event) => setProfile({ ...profile, category: event.target.value })}
                className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500"
              >
                {businessCategories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </label>

            <label className="grid gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Project cost</span>
              <input
                type="number"
                min="0"
                value={profile.projectCost}
                onChange={(event) => setProfile({ ...profile, projectCost: Number(event.target.value) })}
                className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500"
              />
            </label>

            <label className="grid gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Expected loan amount</span>
              <input
                type="number"
                min="0"
                value={profile.loanAmount}
                onChange={(event) => setProfile({ ...profile, loanAmount: Number(event.target.value) })}
                className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500"
              />
            </label>

            <label className="grid gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Monthly income</span>
              <input
                type="number"
                min="0"
                value={profile.monthlyIncome}
                onChange={(event) => setProfile({ ...profile, monthlyIncome: Number(event.target.value) })}
                className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500"
              />
            </label>
          </div>

          <div className="mt-6 rounded-2xl border border-udyam-200 bg-udyam-50 p-4">
            <div className="flex items-center gap-2 text-sm font-bold text-udyam-700">
              <Target size={16} /> Recommendation mode
            </div>
            <div className="mt-3 text-xs leading-5 text-neutral-600">
              {mode === 'scheme'
                ? 'Showing schemes matched to your selected business requirement.'
                : 'Showing loan plan options matched to your repayment and capital requirement.'}
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-udyam-200 bg-white p-4">
            <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wide text-neutral-500">
              <Target size={14} /> Best fit
            </div>
            <div className="mt-2 text-sm font-bold text-udyam-700">
              {bestFit ? bestFit.name : 'No result'}
            </div>
            <div className="mt-1 text-[11px] text-neutral-500">
              {bestFit ? `${bestFit.matchScore}% match` : 'No match found'}
            </div>
          </div>
        </section>

        <section className="soft-card rounded-[28px] border border-udyam-200 p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wide text-udyam-700">
                <Landmark size={16} /> {mode === 'scheme' ? 'Scheme Matches' : 'Loan Plan Matches'}
              </div>
              <div className="mt-2 text-2xl font-bold tracking-tight text-neutral-950">
                {recommendations.length} Recommendation{recommendations.length === 1 ? '' : 's'}
              </div>
            </div>
          </div>

          <div className="mt-5 space-y-4">
            {recommendations.map((item) => (
              <SchemeCard key={item.id} item={item} type={mode} matchScore={item.matchScore} />
            ))}
          </div>
        </section>
      </div>

      <div className="mx-auto mt-5 max-w-5xl">
        <SchemeNotice />
      </div>

      <div className="mx-auto mt-5 max-w-5xl rounded-2xl border border-neutral-100 bg-white/70 p-5">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <div className="text-sm font-semibold text-neutral-900">{t('schemes', 'question')}</div>
            <div className="mt-1 text-xs text-neutral-500">{t('schemes', 'questionText')}</div>
          </div>
          <button type="button" className="green-button">
            {t('schemes', 'try')} <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
