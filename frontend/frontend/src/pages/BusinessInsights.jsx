import { useEffect, useState } from 'react'
import { LoaderCircle, RefreshCw } from 'lucide-react'
import PageHeader from '../components/common/PageHeader'
import LocationFilters from '../components/insights/LocationFilters'
import MarketOverview from '../components/insights/MarketOverview'
import OpportunityPanel from '../components/insights/OpportunityPanel'
import CompetitionSnapshot from '../components/insights/CompetitionSnapshot'
import KeyInsights from '../components/insights/KeyInsights'
import ReportReadiness from '../components/insights/ReportReadiness'
import { getInsights, friendlyError } from '../services/api'
import { useLanguage } from '../context/LanguageContext'

const initialFilters = { state: 'Uttar Pradesh', district: 'Prayagraj', block: 'Soraon', category: 'Dairy', locationId: null, locationText: '' }

export default function BusinessInsights() {
  const { t } = useLanguage()
  const [filters, setFilters] = useState(initialFilters)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async (nextFilters = filters) => {
    if (!nextFilters.locationId) return
    setLoading(true)
    setError('')
    try {
      setData(await getInsights({ location_id: nextFilters.locationId, state: nextFilters.state, district: nextFilters.district, category: nextFilters.category }))
      setFilters(nextFilters)
    } catch (requestError) {
      setData(null)
      setError(friendlyError(requestError, 'Could not load business insights.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // LocationFilters resolves the supported location list and triggers the first load.
  }, [])

  const display = data && data.available ? {
    category: data.category,
    demandScore: data.demand_score,
    competitionScore: data.competition_score,
    competitionCount: data.competition_count,
    opportunityScore: data.opportunity_score,
    averageMarketPrice: data.average_market_price,
    dataDate: data.data_date,
    topOpportunities: data.top_opportunities || [],
    mlBusinessMatches: data.ml_business_matches || [],
    location: data.location,
  } : null

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader title={t('insights', 'title')} subtitle={t('insights', 'subtitle')} />
      <div className="mt-8"><LocationFilters onApply={load} /></div>

      {loading && <div className="mt-5 flex items-center justify-center gap-2 rounded-2xl bg-white/70 p-8 text-sm text-neutral-500"><LoaderCircle size={17} className="animate-spin" /> Preparing local insights…</div>}
      {error && <div role="alert" className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-red-100 bg-red-50 p-4 text-xs text-red-700"><span>{error}</span><button type="button" onClick={() => load()} className="inline-flex items-center gap-1.5 font-semibold"><RefreshCw size={13} /> Retry</button></div>}

      {display && (
        <>
          <div className="mt-5"><MarketOverview data={display} /></div>
          <div className="mt-5 grid gap-4 lg:grid-cols-2"><OpportunityPanel data={display} /><CompetitionSnapshot data={display} /></div>
          <div className="mt-5"><KeyInsights data={display} /></div>
          <ReportReadiness filters={filters} data={display} />
        </>
      )}
    </div>
  )
}
