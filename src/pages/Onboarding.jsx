import { useState } from 'react'
import { ArrowLeft, ArrowRight, MapPin, WalletCards, BriefcaseBusiness, CheckCircle2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useLanguage } from '../context/LanguageContext'

const steps = [
  { key: 'location', icon: MapPin },
  { key: 'business', icon: BriefcaseBusiness },
  { key: 'margin', icon: WalletCards },
]

const initialForm = {
  state: 'Uttar Pradesh',
  district: 'Prayagraj',
  block: 'Soraon',
  category: 'Dairy',
  margin: '100000',
}

export default function Onboarding() {
  const navigate = useNavigate()
  const { t } = useLanguage()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(initialForm)

  const update = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }))
  const next = () => (step === steps.length - 1 ? navigate('/calculator', { state: form }) : setStep((current) => current + 1))

  return (
    <div className="page-container py-10 sm:py-16">
      <div className="mx-auto max-w-3xl">
        <div className="text-center">
          <div className="section-kicker">{t('onboarding', 'kicker')}</div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight text-neutral-950 sm:text-4xl">{t('onboarding', 'title')}</h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-neutral-600">{t('onboarding', 'description')}</p>
        </div>

        <div className="mt-8 grid grid-cols-3 gap-2 sm:gap-4">
          {steps.map((item, index) => {
            const Icon = item.icon
            const active = index === step
            const complete = index < step
            return (
              <div key={item.key} className={`flex items-center gap-2 border-b-2 pb-3 text-xs font-semibold ${active || complete ? 'border-udyam-600 text-udyam-700' : 'border-neutral-200 text-neutral-400'}`}>
                <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full ${complete ? 'bg-udyam-600 text-white' : active ? 'bg-udyam-50 text-udyam-700' : 'bg-neutral-100'}`}>
                  {complete ? <CheckCircle2 size={16} /> : <Icon size={16} />}
                </span>
                <span className="hidden sm:inline">{t('onboarding', item.key)}</span>
              </div>
            )
          })}
        </div>

        <div className="soft-card mt-8 p-5 sm:p-8">
          {step === 0 && (
            <div>
              <h2 className="text-lg font-semibold text-neutral-900">{t('onboarding', 'where')}</h2>
              <p className="mt-1 text-sm text-neutral-500">{t('onboarding', 'locationText')}</p>
              <div className="mt-6 grid gap-4 sm:grid-cols-3">
                <label className="grid gap-1.5"><span className="text-xs font-medium text-neutral-600">{t('onboarding', 'state')}</span><select value={form.state} onChange={update('state')} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400"><option>Uttar Pradesh</option><option>Other</option></select></label>
                <label className="grid gap-1.5"><span className="text-xs font-medium text-neutral-600">{t('onboarding', 'district')}</span><select value={form.district} onChange={update('district')} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400"><option>Prayagraj</option><option>Other</option></select></label>
                <label className="grid gap-1.5"><span className="text-xs font-medium text-neutral-600">{t('onboarding', 'block')}</span><select value={form.block} onChange={update('block')} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400"><option>Soraon</option><option>Other</option></select></label>
              </div>
            </div>
          )}

          {step === 1 && (
            <div>
              <h2 className="text-lg font-semibold text-neutral-900">{t('onboarding', 'what')}</h2>
              <p className="mt-1 text-sm text-neutral-500">{t('onboarding', 'businessText')}</p>
              <label className="mt-6 grid gap-1.5"><span className="text-xs font-medium text-neutral-600">{t('onboarding', 'category')}</span><select value={form.category} onChange={update('category')} className="h-11 rounded-xl border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-udyam-400"><option>Dairy</option><option>Retail</option><option>Food Processing</option><option>Textiles</option><option>Services</option></select></label>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-lg font-semibold text-neutral-900">{t('onboarding', 'howMuch')}</h2>
              <p className="mt-1 text-sm text-neutral-500">{t('onboarding', 'marginText')}</p>
              <label className="mt-6 grid gap-1.5"><span className="text-xs font-medium text-neutral-600">{t('onboarding', 'available')}</span><input type="number" min="0" value={form.margin} onChange={update('margin')} className="h-12 rounded-xl border border-neutral-200 bg-white px-3 text-base outline-none focus:border-udyam-400" /></label>
              <div className="mt-4 rounded-xl bg-[#f2f7ee] p-4 text-xs leading-5 text-neutral-600">{t('onboarding', 'marginNote')}</div>
            </div>
          )}

          <div className="mt-8 flex justify-between gap-3 border-t border-neutral-100 pt-5">
            <button type="button" onClick={() => setStep((current) => Math.max(0, current - 1))} disabled={step === 0} className="ghost-button px-4 py-2.5 text-xs disabled:cursor-not-allowed disabled:opacity-40"><ArrowLeft size={15} /> {t('onboarding', 'back')}</button>
            <button type="button" onClick={next} className="green-button px-4 py-2.5 text-xs">{step === steps.length - 1 ? t('onboarding', 'seeStructure') : t('onboarding', 'continue')} <ArrowRight size={15} /></button>
          </div>
        </div>
      </div>
    </div>
  )
}