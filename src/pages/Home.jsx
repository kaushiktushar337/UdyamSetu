import Hero from '../components/home/Hero'
import HomeUpdates from '../components/home/HomeUpdates'
import FeatureGrid from '../components/home/FeatureGrid'
import QuickLinks from '../components/home/QuickLinks'
import TrustStats from '../components/home/TrustStats'

export default function Home() {
  return (
    <>
      <Hero />
      <FeatureGrid />
      <QuickLinks />
      <TrustStats />
      <HomeUpdates />
    </>
  )
}
