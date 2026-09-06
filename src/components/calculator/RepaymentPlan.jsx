import { useState } from 'react'
import { CalendarDays, Clock3, Percent, WalletCards } from 'lucide-react'
import SectionCard from '../common/SectionCard'
import { useLanguage } from '../../context/LanguageContext'

export default function RepaymentPlan({ result }) {
  const { t } = useLanguage()
  const [view, setView] = useState('monthly')
  const quarterlyPayment = result.emi * 3

  return (
    <SectionCard
      title={t('calculator', 'repayment')}
      subtitle={t('calculator', 'repaymentText')}
    >
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Percent size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">{t('calculator', 'interest')}</div>
          <div className="mt-1 text-sm font-semibold">{result.scheme.interest} p.a.</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <CalendarDays size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">{t('calculator', 'tenure')}</div>
          <div className="mt-1 text-sm font-semibold">{result.scheme.tenure}</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Clock3 size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">{t('calculator', 'moratorium')}</div>
          <div className="mt-1 text-sm font-semibold">{result.scheme.moratorium}</div>
        </div>
      </div>

      <div className="mt-4 rounded-xl bg-[#eef6e9] p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-[11px] font-medium text-neutral-500">
            <WalletCards size={15} className="text-udyam-700" /> {t('calculator', 'payment')}
          </div>
          <div className="inline-flex rounded-lg border border-udyam-200 bg-white p-0.5 text-[11px] font-semibold">
            <button type="button" onClick={() => setView('monthly')} className={`rounded-md px-2.5 py-1 ${view === 'monthly' ? 'bg-udyam-700 text-white' : 'text-udyam-700'}`}>
              {t('calculator', 'monthly')}
            </button>
            <button type="button" onClick={() => setView('quarterly')} className={`rounded-md px-2.5 py-1 ${view === 'quarterly' ? 'bg-udyam-700 text-white' : 'text-udyam-700'}`}>
              {t('calculator', 'quarterly')}
            </button>
          </div>
        </div>
        <div className="mt-1 text-xl font-bold text-udyam-700">
          ₹{(view === 'monthly' ? result.emi : quarterlyPayment).toLocaleString('en-IN')} / {view === 'monthly' ? t('calculator', 'month') : t('calculator', 'quarter')}
        </div>
        <div className="mt-1 text-[10px] leading-4 text-neutral-500">{t('calculator', 'moratoriumText')}</div>
      </div>
    </SectionCard>
  )
}
