import { CheckCircle2, CircleAlert, FileDown, MessageCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useLanguage } from '../../context/LanguageContext'

export default function ReportReadiness({ filters, data }) {
  const { t } = useLanguage()
  const downloadSummary = () => {
    const summary = [
      'UdyamSetu business insights',
      `Location: ${filters.locationText || [filters.block, filters.district, filters.state].filter(Boolean).join(', ')}`,
      `Business category: ${filters.category}`,
      `Demand score: ${data.demandScore ?? 'Not available'}/100`,
      `Opportunity score: ${data.opportunityScore ?? 'Not available'}/100`,
      `Competition score: ${data.competitionScore ?? 'Not available'}/100`,
      `Competition count: ${data.competitionCount ?? 'Not available'}`,
      '',
      'These figures come from UdyamSetu market metrics and are advisory. Verify important assumptions before investing.',
    ].join('\n')
    const url = URL.createObjectURL(new Blob([summary], { type: 'text/plain' }))
    const link = document.createElement('a'); link.href = url; link.download = 'udyamsetu-business-insights.txt'; link.click(); URL.revokeObjectURL(url)
  }
  return <div className="soft-card mt-5 p-5 sm:p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="text-sm font-semibold text-neutral-900">{t('insights', 'readiness')}</div><p className="mt-1 text-xs leading-5 text-neutral-600">Your {filters.category.toLowerCase()} view for {filters.locationText || filters.block} is ready.</p></div><div className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1.5 text-[10px] font-semibold text-amber-700"><CircleAlert size={13} /> Advisory</div></div><div className="mt-5 grid gap-3 sm:grid-cols-3">{['Location and category selected','Market figures come from the database','Verify important assumptions before investing'].map((check) => <div key={check} className="flex gap-2 text-xs leading-5 text-neutral-700"><CheckCircle2 size={15} className="mt-0.5 shrink-0 text-udyam-600" />{check}</div>)}</div><div className="mt-5 flex flex-wrap gap-2 border-t border-neutral-100 pt-4"><button type="button" onClick={downloadSummary} className="ghost-button px-3 py-2 text-xs"><FileDown size={14} /> {t('insights', 'download')}</button><Link to="/assistant" className="green-button px-3 py-2 text-xs"><MessageCircle size={14} /> {t('insights', 'ask')}</Link></div></div>
}
