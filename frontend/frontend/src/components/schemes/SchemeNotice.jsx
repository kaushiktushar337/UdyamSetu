import { useLanguage } from '../../context/LanguageContext'

export default function SchemeNotice() {
  const { t } = useLanguage()

  return (
    <div className="rounded-2xl border border-udyam-100 bg-[#f0f6eb] p-5">
      <div className="text-sm font-semibold text-neutral-900">{t('schemes', 'noticeTitle')}</div>
      <div className="mt-1 text-xs leading-5 text-neutral-600">{t('schemes', 'noticeText')}</div>
    </div>
  )
}
