import { useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import PageHeader from '../components/common/PageHeader'
import CalculatorForm from '../components/calculator/CalculatorForm'
import FinancialResults from '../components/calculator/FinancialResults'
import RepaymentPlan from '../components/calculator/RepaymentPlan'
import { calculateEMI } from '../utils/financialCalculations'
import { calculateStructure } from '../utils/schemeRouter'
import { useLanguage } from '../context/LanguageContext'

const initial = {
  margin: '100000',
  category: 'Dairy',
  location: 'Soraon, Prayagraj, Uttar Pradesh',
}

export default function FinancialCalculator() {
  const { t } = useLanguage()
  const location = useLocation()
  const [form, setForm] = useState(() => ({ ...initial, ...(location.state ?? {}) }))

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
        title={t('calculator', 'title')}
        subtitle={t('calculator', 'subtitle')}
      />

      <div className="mt-8 grid gap-5 lg:grid-cols-[300px_1fr]">
        <CalculatorForm initial={form} onCalculate={setForm} />

        <div className="grid gap-5">
          <div className="soft-card p-5 sm:p-6">
            <div className="text-sm font-semibold text-neutral-900">{t('calculator', 'details')}</div>
            <div className="mt-5">
              <FinancialResults result={result} />
            </div>
          </div>

          <RepaymentPlan result={result} />

          <div className="rounded-2xl border border-neutral-200 bg-white/70 p-4 text-xs leading-5 text-neutral-600">
            <div className="font-semibold text-neutral-900">{t('calculator', 'assumptions')}</div>
            <div className="mt-1">{t('calculator', 'assumptionsText')}</div>
          </div>

          {result.capped && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-800">
              {t('calculator', 'capped')} ₹{result.eligibleProjectCost.toLocaleString('en-IN')}; {t('calculator', 'additional')} ₹{result.additionalMargin.toLocaleString('en-IN')} {t('calculator', 'additionalPath')}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
