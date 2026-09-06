import PageHeader from '../components/common/PageHeader'
import ProcessSteps from '../components/howItWorks/ProcessSteps'
import ImpactStrip from '../components/howItWorks/ImpactStrip'
import { useLanguage } from '../context/LanguageContext'

export default function HowItWorks() {
  const { t } = useLanguage()

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        kicker={t('how', 'kicker')}
        title={t('how', 'title')}
        subtitle={t('how', 'subtitle')}
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
