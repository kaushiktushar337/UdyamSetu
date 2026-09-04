import { CalendarDays, Percent, IndianRupee, Clock3 } from 'lucide-react'

export default function SchemeCard({ scheme }) {
  return (
    <div className="soft-card p-6">
      <div className="text-base font-semibold text-udyam-700">{scheme.name}</div>
      <div className="mt-1 text-xs text-neutral-500">{scheme.summary}</div>

      <div className="mt-5 grid gap-3 sm:grid-cols-4">
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <IndianRupee size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Loan Amount</div>
          <div className="mt-1 text-sm font-semibold">{scheme.loan}</div>
          <div className="mt-1 text-[10px] text-neutral-500">{scheme.loanHelper}</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Percent size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Interest Rate</div>
          <div className="mt-1 text-sm font-semibold">{scheme.interest}</div>
          <div className="mt-1 text-[10px] text-neutral-500">per annum</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <CalendarDays size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Repayment Tenure</div>
          <div className="mt-1 text-sm font-semibold">{scheme.tenure}</div>
          <div className="mt-1 text-[10px] text-neutral-500">maximum</div>
        </div>
        <div className="rounded-xl bg-[#f7faf4] p-4">
          <Clock3 size={17} className="text-udyam-700" />
          <div className="mt-2 text-[11px] text-neutral-500">Moratorium</div>
          <div className="mt-1 text-sm font-semibold">{scheme.moratorium}</div>
          <div className="mt-1 text-[10px] text-neutral-500">before repayment</div>
        </div>
      </div>

      <div className="mt-5 grid gap-5 border-t border-neutral-100 pt-5 md:grid-cols-2">
        <div>
          <div className="text-xs font-semibold text-neutral-900">Who can apply?</div>
          <p className="mt-2 text-xs leading-5 text-neutral-600">{scheme.who}</p>
        </div>
        <div>
          <div className="text-xs font-semibold text-neutral-900">Example</div>
          <p className="mt-2 text-xs leading-5 text-neutral-600">{scheme.example}</p>
        </div>
      </div>
    </div>
  )
}
