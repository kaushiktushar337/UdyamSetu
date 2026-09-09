import { Users, Store, MapPin, Star } from 'lucide-react'
import StatCard from '../common/StatCard'

export default function TrustStats() {
  return (
    <section className="page-container py-8 sm:py-10">
      <div className="rounded-2xl border border-udyam-100 bg-[#edf5e7] p-6 sm:p-8">
        <div className="text-center">
          <div className="text-lg font-semibold text-udyam-800">Empowering Rural India. One Successful Entrepreneur at a Time.</div>
        </div>
        <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard icon={Users} value="10L+" label="Rural Entrepreneurs" />
          <StatCard icon={Store} value="500+" label="Business Categories" />
          <StatCard icon={MapPin} value="5L+" label="Villages Covered" />
          <StatCard icon={Star} value="95%" label="User Satisfaction" />
        </div>
      </div>
    </section>
  )
}
