import { Outlet } from 'react-router-dom'
import Navbar from '../components/common/Navbar'
import Footer from '../components/common/Footer'
import AssistantLauncher from '../components/common/AssistantLauncher'

export default function AppLayout() {
  return (
    <div className="page-shell">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
      <AssistantLauncher />
    </div>
  )
}
