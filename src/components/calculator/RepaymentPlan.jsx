import { CalendarDays, Clock3, Percent, WalletCards } from 'lucide-react'
import SectionCard from '../common/SectionCard'

export default function RepaymentPlan({ result }) {
  return (
    <SectionCard
      title="Repayment Plan (Indicative)"
      subtitle="Monthly EMI shown for planning only. Moratorium treatment may differ under official rules."
    >
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Percent size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Interest Rate</div>
          <div className="mt-1 text-sm font-semibold">{result.scheme.interest} p.a.</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <CalendarDays size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Repayment Tenure</div>
          <div className="mt-1 text-sm font-semibold">{result.scheme.tenure}</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Clock3 size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Moratorium Period</div>
          <div className="mt-1 text-sm font-semibold">{result.scheme.moratorium}</div>
        </div>
      </div>

      <div className="mt-4 rounded-xl bg-[#eef6e9] p-4">
        <div className="flex items-center gap-2 text-[11px] font-medium text-neutral-500">
          <WalletCards size={15} className="text-udyam-700" /> Estimated EMI (After Moratorium)
        </div>
        <div className="mt-1 text-xl font-bold text-udyam-700">₹{result.emi.toLocaleString('en-IN')} / Month</div>
      </div>
    </SectionCard>
  )
}
