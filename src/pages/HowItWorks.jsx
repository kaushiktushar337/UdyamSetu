import PageHeader from '../components/common/PageHeader'
import ProcessSteps from '../components/howItWorks/ProcessSteps'
import ImpactStrip from '../components/howItWorks/ImpactStrip'

export default function HowItWorks() {
  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        kicker="Simple guided journey"
        title="How UdyamSetu Works?"
        subtitle="A simple 4-step journey from idea to successful enterprise."
      />

      <div className="mt-10">
        <ProcessSteps />
      </div>

      <div className="mt-10">
        <ImpactStrip />
      </div>
    </div>
  )
}
