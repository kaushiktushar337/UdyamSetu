import { Link } from 'react-router-dom'
import { useLanguage } from '../../context/LanguageContext'

export default function Footer() {
  const { t } = useLanguage()

  return (
    <footer className="border-t border-udyam-100 bg-white/80">
      <div className="page-container grid gap-8 py-10 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-udyam-50">
              <img className='object-cover' src="/udyamsetu-logo.png" alt="UdyamSetuLogo" />
            </div>
            <div>
              <div className="font-serif text-lg font-semibold text-udyam-800">UdyamSetu</div>
              <div className="text-xs text-neutral-500">{t('footer', 'tagline')}</div>
            </div>
          </div>
          <p className="mt-4 max-w-sm text-sm leading-6 text-neutral-600">
            {t('footer', 'description')}
          </p>
        </div>

        <div>
          <div className="text-sm font-semibold text-neutral-900">{t('footer', 'explore')}</div>
          <div className="mt-3 grid gap-2 text-sm text-neutral-600">
            <Link to="/how-it-works" className="hover:text-udyam-700">{t('footer', 'how')}</Link>
            <Link to="/schemes" className="hover:text-udyam-700">{t('footer', 'schemes')}</Link>
            <Link to="/insights" className="hover:text-udyam-700">{t('footer', 'insights')}</Link>
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-neutral-900">{t('footer', 'important')}</div>
          <p className="mt-3 text-sm leading-6 text-neutral-600">
            {t('footer', 'disclaimer')}
          </p>
        </div>
      </div>
      <div className="border-t border-neutral-100 py-4">
        <div className="page-container text-xs text-neutral-500">© 2026 UdyamSetu</div>
      </div>
    </footer>
  )
}
