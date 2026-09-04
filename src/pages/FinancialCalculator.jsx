import { useMemo, useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import CalculatorForm from '../components/calculator/CalculatorForm'
import FinancialResults from '../components/calculator/FinancialResults'
import RepaymentPlan from '../components/calculator/RepaymentPlan'
import { calculateEMI } from '../utils/financialCalculations'
import { calculateStructure } from '../utils/schemeRouter'

const initial = {
  margin: '100000',
  category: 'Dairy',
  location: 'Soraon, Prayagraj, Uttar Pradesh',
}

export default function FinancialCalculator() {
  const [form, setForm] = useState(initial)

  const result = useMemo(() => {
    const structure = calculateStructure(form.margin)
    return {
      ...structure,
      emi: calculateEMI(structure.loanAmount, structure.scheme.interestRate, structure.scheme.tenureYears),
    }
  }, [form.margin])

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
        title="Financial Calculator"
        subtitle="Calculate your project cost, loan amount and repayment details."
      />

      <div className="mt-8 grid gap-5 lg:grid-cols-[300px_1fr]">
        <CalculatorForm initial={form} onCalculate={setForm} />

        <div className="grid gap-5">
          <div className="soft-card p-5 sm:p-6">
            <div className="text-sm font-semibold text-neutral-900">Results for You</div>
            <div className="mt-5">
              <FinancialResults result={result} />
            </div>
          </div>

          <RepaymentPlan result={result} />

          {result.capped && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-800">
              Your theoretical project cost exceeds the maximum supported structure. This prototype shows the scheme cap; additional own contribution or an alternative financing path would be needed.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
