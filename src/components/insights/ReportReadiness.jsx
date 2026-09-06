import { CheckCircle2, CircleAlert, FileDown, MessageCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useLanguage } from '../../context/LanguageContext'

const checks = [
  'Location and business category selected',
  'Market figures labelled as model estimates',
  'Scheme terms require official verification',
]

export default function ReportReadiness({ filters }) {
  const { t } = useLanguage()
  const downloadSummary = () => {
    const summary = [
      'UdyamSetu feasibility summary',
      `Location: ${filters.block}, ${filters.district}, ${filters.state}`,
      `Business category: ${filters.category}`,
      '',
      'This is an advisory estimate based on prototype market data.',
      'Verify all scheme terms, eligibility, and local assumptions with the authorized agency.',
    ].join('\n')
    const url = URL.createObjectURL(new Blob([summary], { type: 'text/plain' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'udyamsetu-feasibility-summary.txt'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="soft-card mt-5 p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-neutral-900">{t('insights', 'readiness')}</div>
          <p className="mt-1 text-xs leading-5 text-neutral-600">Your {filters.category.toLowerCase()} assessment for {filters.block}, {filters.district} is ready for review.</p>
        </div>
        <div className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1.5 text-[10px] font-semibold text-amber-700"><CircleAlert size={13} /> {t('insights', 'advisory')}</div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        {checks.map((check) => <div key={check} className="flex gap-2 text-xs leading-5 text-neutral-700"><CheckCircle2 size={15} className="mt-0.5 shrink-0 text-udyam-600" />{check}</div>)}
      </div>

      <div className="mt-5 flex flex-wrap gap-2 border-t border-neutral-100 pt-4">
        <button type="button" onClick={downloadSummary} className="ghost-button px-3 py-2 text-xs"><FileDown size={14} /> {t('insights', 'download')}</button>
        <Link to="/assistant" className="green-button px-3 py-2 text-xs"><MessageCircle size={14} /> {t('insights', 'ask')}</Link>
      </div>
    </div>
  )
}