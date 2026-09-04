import { Link, NavLink } from 'react-router-dom'
import { ArrowRight, ChevronDown } from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'How it works', to: '/how-it-works' },
  { label: 'Schemes', to: '/schemes' },
  { label: 'Business Insights', to: '/insights' },
  { label: 'Calculator', to: '/calculator' },
  { label: 'AI Assistant', to: '/assistant' },
]

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-udyam-100/70 bg-white/90 backdrop-blur">
      <div className="page-container flex h-[72px] items-center justify-between gap-4">
        <Link to="/" className="flex shrink-0 items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-udyam-50 text-lg">🌾</div>
          <div className="leading-tight">
            <div className="font-serif text-[25px] font-semibold tracking-tight text-neutral-900">UdyamSetu</div>
            <div className="text-[12px] font-medium text-neutral-600">Sapno se saathi, safal udyam ki ore</div>
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
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          <button className="inline-flex items-center gap-1 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs text-neutral-700">
            <span>🌐</span> English <ChevronDown size={13} />
          </button>
          <Link to="/calculator" className="green-button px-4 py-2.5 text-xs">
            Get Started <ArrowRight size={14} />
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
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </header>
  )
}
