import { useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import LocationFilters from '../components/insights/LocationFilters'
import MarketOverview from '../components/insights/MarketOverview'
import OpportunityPanel from '../components/insights/OpportunityPanel'
import CompetitionSnapshot from '../components/insights/CompetitionSnapshot'
import KeyInsights from '../components/insights/KeyInsights'
import ReportReadiness from '../components/insights/ReportReadiness'
import { getMarketData } from '../data/marketData'
import { useLanguage } from '../context/LanguageContext'

const initialFilters = { state: 'Uttar Pradesh', district: 'Prayagraj', block: 'Soraon', category: 'Dairy' }

export default function BusinessInsights() {
  const { t } = useLanguage()
  const [filters, setFilters] = useState(initialFilters)
  const data = { ...getMarketData(filters), category: filters.category }

  const handleApply = (nextFilters) => setFilters(nextFilters)

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        title={t('insights', 'title')}
        subtitle={`${t('insights', 'subtitle')} ${filters.block}, ${filters.district}.`}
      />

      <div className="mt-8">
        <LocationFilters onApply={handleApply} />
      </div>

      <div className="mt-5">
        <MarketOverview data={data} />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <OpportunityPanel data={data} />
        <CompetitionSnapshot data={data} />
      </div>

      <div className="mt-5">
        <KeyInsights />
      </div>

      <ReportReadiness filters={filters} />
    </div>
  )
}
