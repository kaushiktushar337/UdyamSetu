import { ArrowRight, PlayCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useLanguage } from '../../context/LanguageContext'

const heroImages = ['farmer.png', 'shop.png', 'tailor.png', 'electrician.png', 'gardener.png', 'milkman.png']

const heroImageMeta = {
  'farmer.png': { label: 'Farm Growth', demand: 'Organic produce demand' },
  'shop.png': { label: 'Retail Growth', demand: 'Daily essentials demand' },
  'tailor.png': { label: 'Service Growth', demand: 'Custom clothing demand' },
  'electrician.png': { label: 'Skill Growth', demand: 'Repair services demand' },
  'gardener.png': { label: 'Green Growth', demand: 'Urban gardening demand' },
  'milkman.png': { label: 'Dairy Growth', demand: 'Fresh milk demand' },
}

export default function Hero() {
  const { t } = useLanguage()
  const [farmerHovered, setFarmerHovered] = useState(false)
  const [activeImage, setActiveImage] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveImage((current) => (current + 1) % heroImages.length)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

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
              <div
                className="relative z-30 h-[330px] w-full overflow-visible"
                onMouseEnter={() => setFarmerHovered(true)}
                onMouseLeave={() => setFarmerHovered(false)}
              >
                <div className="absolute bottom-[-16px] right-[-8px] h-[420px] w-[420px] overflow-hidden">
                  {heroImages.map((image, index) => (
                    <img
                      key={image}
                      src={`/${image}`}
                      alt={image.replace('.png', '')}
                      className={`absolute bottom-0 right-0 h-[420px] w-auto object-contain drop-shadow-[0_25px_30px_rgba(0,0,0,0.22)] transition-all duration-700 ease-out ${
                        index === activeImage ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95'
                      }`}
                      style={{
                        marginRight: '-14px',
                        transform: farmerHovered && index === activeImage ? 'translateY(-8px) scale(1.04)' : 'translateY(0) scale(1)',
                      }}
                    />
                  ))}
                </div>
              </div>

              <div className="absolute left-1/2 top-[calc(100%-10px)] z-40 flex -translate-x-1/2 items-center justify-center gap-2 rounded-full border border-white/70 bg-white/80 px-3 py-2 shadow-sm backdrop-blur">
                {heroImages.map((image, index) => (
                  <button
                    key={image}
                    type="button"
                    aria-label={`Show ${image.replace('.png', '')}`}
                    onClick={() => setActiveImage(index)}
                    className={`h-3 w-3 rounded-full border transition-all duration-300 ${
                      index === activeImage ? 'h-3.5 w-3.5 border-udyam-700 bg-udyam-700' : 'border-udyam-700/60 bg-white hover:bg-udyam-100'
                    }`}
                  />
                ))}
              </div>

              <div className="absolute bottom-6 left-6 z-40 rounded-2xl border border-white/80 bg-white/90 px-4 py-3 shadow-sm backdrop-blur">
                <div className="text-[10px] font-semibold uppercase tracking-wide text-neutral-500">
                  {heroImageMeta[heroImages[activeImage]].label}
                </div>

                <div className="mt-1 text-sm font-bold text-udyam-700">
                  {heroImageMeta[heroImages[activeImage]].demand}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
