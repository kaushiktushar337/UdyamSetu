import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import Home from './pages/Home'
import HowItWorks from './pages/HowItWorks'
import Schemes from './pages/Schemes'
import BusinessInsights from './pages/BusinessInsights'
import FinancialCalculator from './pages/FinancialCalculator'
import AIAssistant from './pages/AIAssistant'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/schemes" element={<Schemes />} />
        <Route path="/insights" element={<BusinessInsights />} />
        <Route path="/calculator" element={<FinancialCalculator />} />
        <Route path="/assistant" element={<AIAssistant />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
