import { Link, NavLink } from 'react-router-dom'
import { ArrowRight, ChevronDown, Globe2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { languages, useLanguage } from '../../context/LanguageContext'

const navItems = [
  { key: 'home', to: '/' },
  { key: 'how', to: '/how-it-works' },
  { key: 'schemes', to: '/schemes' },
  { key: 'insights', to: '/insights' },
  { key: 'calculator', to: '/calculator' },
  { key: 'assistant', to: '/assistant' },
]

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [languageOpen, setLanguageOpen] = useState(false)
  const [scrollProgress, setScrollProgress] = useState(0)
  const { language, languageLabel, setLanguage, t } = useLanguage()

  useEffect(() => {
    const updateScrollProgress = () => {
      const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = scrollableHeight > 0 ? (window.scrollY / scrollableHeight) * 100 : 0
      setScrollProgress(Math.min(100, Math.max(0, progress)))
    }

    updateScrollProgress()
    window.addEventListener('scroll', updateScrollProgress, { passive: true })
    window.addEventListener('resize', updateScrollProgress)

    return () => {
      window.removeEventListener('scroll', updateScrollProgress)
      window.removeEventListener('resize', updateScrollProgress)
    }
  }, [])

  return (
    <header className="sticky top-0 z-50 border-b border-udyam-100/70 bg-green-50 backdrop-blur">
      <div
        aria-label="Page scroll progress"
        className="fixed inset-x-0 top-0 z-[60] h-1 bg-udyam-100/60"
        role="progressbar"
        aria-valuemax="100"
        aria-valuemin="0"
        aria-valuenow={Math.round(scrollProgress)}
      >
        <div
          className="h-full bg-udyam-600 transition-[width] duration-150 ease-out"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>
      <div className="page-container flex h-[72px] items-center justify-between gap-4">
        <Link to="/" className="flex shrink-0 items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-udyam-50 text-lg">
            <img className='object-cover' src="/UdyamSetuLogo.png" alt="UdyamSetuLogo" />
          </div>
          <div className="leading-tight">
            <div className="font-serif text-[25px] font-semibold tracking-tight text-udyam-800">UdyamSetu</div>
            <div className="text-[12px] font-medium text-neutral-600">Sapno ka saathi, safal udyam ki ore</div>
          </div>
        </Link>

        <nav className="hidden items-center gap-5 lg:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `text-[12px] font-medium transition ${
                  isActive ? 'text-udyam-700 underline decoration-2 underline-offset-8' : 'text-neutral-700 hover:text-udyam-700'
                }`
              }
            >
              {t('nav', item.key)}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          <div className="relative">
            <button
              type="button"
              aria-expanded={languageOpen}
              onClick={() => setLanguageOpen((current) => !current)}
              className="inline-flex items-center gap-1 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs text-neutral-700"
            >
              <Globe2 size={14} /> {languageLabel} <ChevronDown size={13} />
            </button>
            {languageOpen && (
              <div className="absolute right-0 top-11 z-10 w-32 rounded-xl border border-neutral-100 bg-white p-1 shadow-soft">
                {languages.map((option) => (
                  <button
                    type="button"
                    key={option.code}
                    onClick={() => { setLanguage(option.code); setLanguageOpen(false) }}
                    className={`block w-full rounded-lg px-3 py-2 text-left text-xs ${language === option.code ? 'bg-udyam-50 font-semibold text-udyam-700' : 'text-neutral-700 hover:bg-neutral-50'}`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          <Link to="/start" className="green-button px-4 py-2.5 text-xs">
            {t('nav', 'getStarted')} <ArrowRight size={14} />
          </Link>
        </div>

        <button
          className="rounded-lg border border-neutral-200 px-3 py-2 text-sm lg:hidden"
          onClick={() => setMenuOpen((value) => !value)}
        >
          Menu
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-neutral-100 bg-white lg:hidden">
          <div className="page-container grid gap-1 py-3">
            {navItems.map((item) => (
              <NavLink
                onClick={() => setMenuOpen(false)}
                key={item.to}
                to={item.to}
                className="rounded-lg px-3 py-3 text-sm text-neutral-700 hover:bg-udyam-50"
              >
                {t('nav', item.key)}
              </NavLink>
            ))}
            <div className="mt-2 border-t border-neutral-100 pt-3">
              <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-neutral-400">{t('nav', 'language')}</div>
              <div className="flex flex-wrap gap-2">
                {languages.map((option) => (
                  <button type="button" key={option.code} onClick={() => setLanguage(option.code)} className={`rounded-lg px-3 py-2 text-xs ${language === option.code ? 'bg-udyam-50 font-semibold text-udyam-700' : 'bg-neutral-50 text-neutral-700'}`}>
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
