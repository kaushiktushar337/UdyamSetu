import { useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import CalculatorForm from '../components/calculator/CalculatorForm'
import FinancialResults from '../components/calculator/FinancialResults'
import RepaymentPlan from '../components/calculator/RepaymentPlan'
import AIAnalysisCard from '../components/calculator/AIAnalysisCard'
import { calculateEMI } from '../utils/financialCalculations'
import { calculateStructure } from '../utils/schemeRouter'
import { analyzeBusiness, friendlyError, getLatestUserLocation, getUserId } from '../services/api'
import { useLanguage } from '../context/LanguageContext'

const initial = { margin: '100000', category: 'Dairy', location: 'Soraon, Prayagraj, Uttar Pradesh', locationId: null }

export default function FinancialCalculator() {
  const { t } = useLanguage()
  const routeLocation = useLocation()
  const [form, setForm] = useState(() => ({ ...initial, ...(routeLocation.state ?? {}) }))
  const [analysis, setAnalysis] = useState(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState('')

  useEffect(() => {
    if (form.locationId) return
    getLatestUserLocation(getUserId()).then((data) => {
      if (data?.location_id || data?.estimated_address) setForm((current) => ({ ...current, locationId: data.location_id || current.locationId, location: data.estimated_address || current.location }))
    }).catch(() => {})
  }, [form.locationId, form.locationText])

  const structure = calculateStructure(form.margin)
  const result = { ...structure, emi: calculateEMI(structure.loanAmount, structure.scheme.interestRate, structure.scheme.tenureYears) }

  const runAnalysis = async () => {
    setAnalysisLoading(true); setAnalysisError('')
    try {
      const data = await analyzeBusiness({
        user_id: getUserId(), available_capital: Number(form.margin) || 0, funding_available: Number(form.margin) || 0,
        interests: form.category, skills: '', experience_years: 0, available_resources: [], infrastructure: [],
        location: form.location || null, location_id: form.locationId || null, preferences: form.category,
        top_k: 5, persist: false,
      })
      setAnalysis(data)
    } catch (requestError) {
      setAnalysis(null); setAnalysisError(friendlyError(requestError, 'The AI analysis could not be completed. Please try again.'))
    } finally { setAnalysisLoading(false) }
  }

  const updateForm = (next) => setForm(next)

  return <div className="page-container py-12 sm:py-16"><PageHeader title={t('calculator', 'title')} subtitle={t('calculator', 'subtitle')} />
    <div className="mt-8 grid gap-5 lg:grid-cols-[300px_1fr]"><CalculatorForm initial={form} onCalculate={updateForm} />
      <div className="grid gap-5"><div className="soft-card p-5 sm:p-6"><div className="text-sm font-semibold text-neutral-900">{t('calculator', 'details')}</div><div className="mt-5"><FinancialResults result={result} /></div></div>
        <RepaymentPlan result={result} />
        <AIAnalysisCard result={analysis} loading={analysisLoading} error={analysisError} onAnalyze={runAnalysis} />
        <div className="rounded-2xl border border-neutral-200 bg-white/70 p-4 text-xs leading-5 text-neutral-600"><div className="font-semibold text-neutral-900">{t('calculator', 'assumptions')}</div><div className="mt-1">{t('calculator', 'assumptionsText')}</div></div>
        {result.capped && <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-800">{t('calculator', 'capped')} ₹{result.eligibleProjectCost.toLocaleString('en-IN')}; {t('calculator', 'additional')} ₹{result.additionalMargin.toLocaleString('en-IN')} {t('calculator', 'additionalPath')}</div>}
      </div></div>
  </div>
}
