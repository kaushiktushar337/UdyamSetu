import { ArrowRight, PlayCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useLanguage } from '../../context/LanguageContext'

export default function Hero() {
  const { t } = useLanguage()
  const [farmerHovered, setFarmerHovered] = useState(false)

  return (
    <section className="pt-8 sm:pt-10">
      <div className="page-container">
        <div className="relative overflow-hidden rounded-[28px] border border-udyam-100/80 bg-gradient-to-br from-white via-[#f4f8ef] to-[#e8f1e2] p-6 shadow-soft sm:p-10 lg:min-h-[430px]">
          <div className="grid items-center gap-8 lg:grid-cols-[1.02fr_.98fr]">
            <div className="relative z-10">
              <div className="section-kicker">🌱 {t('home', 'kicker')}</div>
              <h1 className="mt-5 max-w-xl text-4xl font-extrabold leading-[1.02] tracking-tight text-neutral-950 sm:text-5xl lg:text-[54px]">
                Aapke Sapno ka <p><span className="text-udyam-600">Sahi Business Saathi</span></p>
              </h1>
              <p className="mt-5 max-w-xl text-sm leading-6 text-neutral-700 sm:text-base">
                {t('home', 'description')}
              </p>
              <div className="mt-7 flex flex-wrap gap-3">
                <Link to="/start" className="green-button">
                  {t('home', 'start')} <ArrowRight size={17} />
                </Link>
                <Link to="/how-it-works" className="ghost-button">
                  <PlayCircle size={18} /> {t('home', 'how')}
                </Link>
              </div>
            </div>

            <div className="relative min-h-[280px] sm:min-h-[330px] overflow-visible">

  {/* Farmer */}
  <div
    className="relative z-30 h-[330px] w-full overflow-visible"
    onMouseEnter={() => setFarmerHovered(true)}
    onMouseLeave={() => setFarmerHovered(false)}
  >
    <img
      src="/farmer.png"
      alt="farmer"
      className="
        absolute
        bottom-0
        right-0
        h-[340px]
        w-auto
        object-contain
        drop-shadow-[0_20px_25px_rgba(0,0,0,0.22)]
        transition-transform duration-300 ease-out
      "
      style={{ transform: farmerHovered ? 'translateY(-14px) scale(1.08)' : 'translateY(0) scale(1)' }}
    />
  </div>

  {/* Local Insight */}
  <div className="absolute bottom-6 left-6 z-40 rounded-2xl border border-white/80 bg-white/90 px-4 py-3 shadow-sm backdrop-blur">
    <div className="text-[10px] font-semibold uppercase tracking-wide text-neutral-500">
      {t('home', 'local')}
    </div>

    <div className="mt-1 text-sm font-bold text-udyam-700">
      {t('home', 'demand')}
    </div>
  </div>

</div>
          </div>
        </div>
      </div>
    </section>
  )
}
