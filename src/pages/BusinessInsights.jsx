import PageHeader from '../components/common/PageHeader'
import LocationFilters from '../components/insights/LocationFilters'
import MarketOverview from '../components/insights/MarketOverview'
import OpportunityPanel from '../components/insights/OpportunityPanel'
import CompetitionSnapshot from '../components/insights/CompetitionSnapshot'
import KeyInsights from '../components/insights/KeyInsights'

export default function BusinessInsights() {
  const handleApply = () => {}

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        title="Business Insights"
        subtitle="Get hyper-local market insights for your business."
      />

      <div className="mt-8">
        <LocationFilters onApply={handleApply} />
      </div>

      <div className="mt-5">
        <MarketOverview />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <OpportunityPanel />
        <CompetitionSnapshot />
      </div>

      <div className="mt-5">
        <KeyInsights />
      </div>
    </div>
  )
}
