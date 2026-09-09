import { CalendarDays, Percent, IndianRupee, Clock3, TrendingUp, CheckCircle, ExternalLink } from 'lucide-react'
import { useLanguage } from '../../context/LanguageContext'

export default function SchemeCard({ item, type = 'scheme', matchScore = 90 }) {
  const { t } = useLanguage()
  const cardTitle = type === 'loanPlan' ? 'Loan Plan' : 'Scheme'

  return (
    <div className="soft-card rounded-[24px] border border-udyam-200 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-udyam-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-udyam-700">
              {cardTitle}
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wide text-neutral-500">Match Score</span>
          </div>
          <div className="mt-3 text-base font-bold text-udyam-700">{item.name}</div>
          <div className="mt-1 text-xs text-neutral-500">{item.summary}</div>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-udyam-200 bg-udyam-50 px-3 py-2">
          <TrendingUp size={15} className="text-udyam-700" />
          <span className="text-sm font-bold text-udyam-700">{matchScore}%</span>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-4">
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <IndianRupee size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">{t('schemes', 'loanAmount')}</div>
          <div className="mt-1 text-sm font-semibold">{item.loan}</div>
          <div className="mt-1 text-[10px] text-neutral-500">{item.loanHelper}</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Percent size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">{t('schemes', 'interestRate')}</div>
          <div className="mt-1 text-sm font-semibold">{item.interest}</div>
          <div className="mt-1 text-[10px] text-neutral-500">{t('common', 'perAnnum')}</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <CalendarDays size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Repayment Tenure</div>
          <div className="mt-1 text-sm font-semibold">{item.tenure}</div>
          <div className="mt-1 text-[10px] text-neutral-500">{t('common', 'maximum')}</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Clock3 size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Moratorium</div>
          <div className="mt-1 text-sm font-semibold">{item.moratorium}</div>
          <div className="mt-1 text-[10px] text-neutral-500">{t('common', 'beforeRepayment')}</div>
        </div>
      </div>

      <div className="mt-5 grid gap-5 border-t border-neutral-100 pt-5 md:grid-cols-2">
        <div>
          <div className="text-xs font-semibold text-neutral-900">{t('common', 'whoApply')}</div>
          <p className="mt-2 text-xs leading-5 text-neutral-600">{item.who}</p>
        </div>
        <div>
          <div className="text-xs font-semibold text-neutral-900">{t('common', 'example')}</div>
          <p className="mt-2 text-xs leading-5 text-neutral-600">{item.example}</p>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-4 border-t border-neutral-100 pt-4">
        <span className="inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-wide text-udyam-700">
          <CheckCircle size={14} /> Best action
        </span>
        <a
          href={item.applyUrl || '#'}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-xl bg-udyam-700 px-4 py-2 text-xs font-bold text-white transition hover:bg-udyam-600"
        >
          Apply <ExternalLink size={14} />
        </a>
      </div>
    </div>
  )
}
