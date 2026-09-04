import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-udyam-100 bg-white/80">
      <div className="page-container grid gap-8 py-10 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-udyam-50">🌾</div>
            <div>
              <div className="font-serif text-lg font-semibold">UdyamSetu</div>
              <div className="text-xs text-neutral-500">AI-driven rural business advisory</div>
            </div>
          </div>
          <p className="mt-4 max-w-sm text-sm leading-6 text-neutral-600">
            Hyper-local market intelligence, transparent financial rules and multilingual assistance for first-time entrepreneurs.
          </p>
        </div>

        <div>
          <div className="text-sm font-semibold text-neutral-900">Explore</div>
          <div className="mt-3 grid gap-2 text-sm text-neutral-600">
            <Link to="/how-it-works" className="hover:text-udyam-700">How it works</Link>
            <Link to="/schemes" className="hover:text-udyam-700">Government schemes</Link>
            <Link to="/insights" className="hover:text-udyam-700">Business insights</Link>
          </div>
        </div>

        <div>
          <div className="text-sm font-semibold text-neutral-900">Important</div>
          <p className="mt-3 text-sm leading-6 text-neutral-600">
            Calculations shown in this prototype are indicative estimates. Official eligibility, appraisal and approval always depend on the authorized agency.
          </p>
        </div>
      </div>
      <div className="border-t border-neutral-100 py-4">
        <div className="page-container text-xs text-neutral-500">© 2026 UdyamSetu</div>
      </div>
    </footer>
  )
}
