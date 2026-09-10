import { MessageCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useLanguage } from '../../context/LanguageContext'

export default function AssistantLauncher() {
  const { t } = useLanguage()

  return (
    <Link
      to="/assistant"
      aria-label={t('assistant', 'name')}
      title={t('assistant', 'name')}
      className="group fixed bottom-5 right-5 z-[60] grid h-14 w-14 place-items-center rounded-full bg-udyam-700 text-white shadow-[0_12px_30px_rgba(47,107,45,0.3)] transition hover:-translate-y-1 hover:bg-udyam-800 focus:outline-none focus:ring-4 focus:ring-udyam-200 sm:bottom-7 sm:right-7"
    >
      <MessageCircle size={23} strokeWidth={2.2} />
      <span className="absolute -right-0.5 -top-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-emerald-400" />
      <span className="pointer-events-none absolute bottom-full right-0 mb-3 whitespace-nowrap rounded-lg bg-neutral-900 px-3 py-2 text-xs font-medium text-white opacity-0 shadow-lg transition group-hover:opacity-100 group-focus-visible:opacity-100">
        {t('assistant', 'name')}
      </span>
    </Link>
  )
}