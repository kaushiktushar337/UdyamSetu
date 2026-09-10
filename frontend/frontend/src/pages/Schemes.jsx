import { useEffect, useState } from 'react'
import { ArrowRight, Landmark, Search, Target, LoaderCircle } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import SchemeCard from '../components/schemes/SchemeCard'
import SchemeNotice from '../components/schemes/SchemeNotice'
import { businessCategories } from '../data/businessCategories'
import { useLanguage } from '../context/LanguageContext'
import { getFundingRecommendations, getLocations, friendlyError } from '../services/api'
import CurrentLocationButton from '../components/common/CurrentLocationButton'

const initialProfile = { category: 'Dairy', projectCost: '', monthlyIncome: '', loanAmount: '', state: '', district: '', locationText: '' }

export default function Schemes() {
  const { t } = useLanguage()
  const [mode, setMode] = useState('scheme')
  const [profile, setProfile] = useState(initialProfile)
  const [locations, setLocations] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingLocations, setLoadingLocations] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getLocations().then((data) => setLocations(Array.isArray(data?.locations) ? data.locations : [])).catch(() => {}).finally(() => setLoadingLocations(false))
  }, [])

  const run = async () => {
    setLoading(true); setError('')
    try {
      const data = await getFundingRecommendations({ category: profile.category, project_cost: Number(profile.projectCost) || null, loan_amount: Number(profile.loanAmount) || null, state: profile.state || null, district: profile.district || null, limit: 8 })
      setRecommendations(mode === 'scheme' ? (data?.schemes || []) : (data?.loans || []))
    } catch (requestError) {
      setRecommendations([]); setError(friendlyError(requestError, 'Could not load funding options.'))
    } finally { setLoading(false) }
  }

  useEffect(() => { run() }, [mode])

  const setLocation = (location) => {
    if (!location) return
    setProfile((current) => ({ ...current, state: location.state || '', district: location.district || '', locationText: [location.location_name, location.district, location.state].filter(Boolean).join(', ') }))
  }

  const resolveCurrentLocation = (result) => {
    const address = result?.estimated_address || ''
    setProfile((current) => ({ ...current, locationText: address }))
    if (result?.location_id) {
      const match = locations.find((item) => String(item.location_id) === String(result.location_id))
      if (match) setLocation(match)
    }
  }

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader title={t('schemes', 'title')} subtitle={t('schemes', 'subtitle')} />
      <div className="mt-8 grid gap-8 xl:grid-cols-[420px_minmax(420px,1fr)]">
        <section className="soft-card rounded-[28px] border border-udyam-200 p-6">
          <div className="flex items-center justify-between"><div><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-udyam-700"><Target size={16} /> Assessment</div><div className="mt-2 text-2xl font-bold tracking-tight text-neutral-950">Find your fit</div></div><div className="rounded-2xl bg-udyam-50 p-2 text-udyam-700"><Search size={20} /></div></div>
          <div className="mt-5 flex rounded-2xl border border-udyam-200 bg-udyam-50 p-1"><button type="button" onClick={() => setMode('scheme')} className={`flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition ${mode === 'scheme' ? 'bg-udyam-700 text-white shadow-soft' : 'text-udyam-700 hover:bg-white'}`}>Schemes</button><button type="button" onClick={() => setMode('loanPlan')} className={`flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition ${mode === 'loanPlan' ? 'bg-udyam-700 text-white shadow-soft' : 'text-udyam-700 hover:bg-white'}`}>Loan Plans</button></div>
          <div className="mt-6 space-y-4">
            <label className="grid gap-2"><span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Business category</span><select value={profile.category} onChange={(event) => setProfile({ ...profile, category: event.target.value })} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500">{businessCategories.map((category) => <option key={category}>{category}</option>)}</select></label>
            <label className="grid gap-2"><span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Project cost</span><input type="number" min="0" value={profile.projectCost} onChange={(event) => setProfile({ ...profile, projectCost: event.target.value })} placeholder="e.g. 500000" className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500" /></label>
            {mode === 'loanPlan' && <label className="grid gap-2"><span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Loan amount</span><input type="number" min="0" value={profile.loanAmount} onChange={(event) => setProfile({ ...profile, loanAmount: event.target.value })} placeholder="e.g. 400000" className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500" /></label>}
            {loadingLocations ? <div className="flex items-center gap-2 text-xs text-neutral-500"><LoaderCircle size={14} className="animate-spin" /> Loading locations…</div> : <label className="grid gap-2"><span className="text-[11px] font-bold uppercase tracking-wide text-neutral-600">Location</span><select value={profile.locationText} onChange={(event) => setLocation(locations.find((item) => [item.location_name, item.district, item.state].filter(Boolean).join(', ') === event.target.value))} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-500"><option value="">Choose an area</option>{locations.map((item) => <option key={item.location_id}>{[item.location_name, item.district, item.state].filter(Boolean).join(', ')}</option>)}</select></label>}
            <CurrentLocationButton onResolved={resolveCurrentLocation} />
            {profile.locationText && <div className="rounded-xl bg-[#f2f7ee] p-3 text-xs text-neutral-600"><span className="font-semibold text-neutral-900">Selected area:</span> {profile.locationText}</div>}
            <button type="button" onClick={run} disabled={loading} className="green-button w-full disabled:opacity-60">{loading ? 'Finding matches…' : 'Find matching options'}</button>
          </div>
        </section>

        <section className="soft-card rounded-[28px] border border-udyam-200 p-6">
          <div className="flex flex-wrap items-center justify-between gap-4"><div><div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wide text-udyam-700"><Landmark size={16} /> {mode === 'scheme' ? 'Scheme matches' : 'Loan plan matches'}</div><div className="mt-2 text-2xl font-bold tracking-tight text-neutral-950">{recommendations.length} recommendation{recommendations.length === 1 ? '' : 's'}</div></div></div>
          {error && <div role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-xs text-red-700">{error}</div>}
          {loading && <div className="mt-6 flex items-center justify-center gap-2 p-8 text-sm text-neutral-500"><LoaderCircle size={17} className="animate-spin" /> Checking the latest database entries…</div>}
          {!loading && !recommendations.length && !error && <div className="mt-6 rounded-2xl bg-neutral-50 p-6 text-center text-sm text-neutral-500">No matching options were returned. Add the relevant scheme or loan records to the database and try again.</div>}
          <div className="mt-5 space-y-4">{recommendations.map((item, index) => <SchemeCard key={item.id || item.loan_plan_id || index} item={item} type={mode} matchScore={item.match_score} />)}</div>
        </section>
      </div>
      <div className="mx-auto mt-5 max-w-5xl"><SchemeNotice /></div>
      <div className="mx-auto mt-5 max-w-5xl rounded-2xl border border-neutral-100 bg-white/70 p-5"><div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center"><div><div className="text-sm font-semibold text-neutral-900">Need help choosing?</div><div className="mt-1 text-xs text-neutral-500">Ask the assistant to explain a scheme or loan plan in simple language.</div></div><a href="/assistant" className="green-button">Ask the assistant <ArrowRight size={16} /></a></div></div>
    </div>
  )
}
