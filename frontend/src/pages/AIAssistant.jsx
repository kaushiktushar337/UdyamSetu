import { useEffect, useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import ChatMessageList from '../components/assistant/ChatMessageList'
import SuggestedQuestions from '../components/assistant/SuggestedQuestions'
import ChatInput from '../components/assistant/ChatInput'
import AssistantPanel from '../components/assistant/AssistantPanel'
import CurrentLocationButton from '../components/common/CurrentLocationButton'
import { chat, getChatHistory, getLatestUserLocation, getUserId, friendlyError } from '../services/api'
import { useLanguage } from '../context/LanguageContext'

const welcome = { role: 'assistant', content: 'Namaste! 👋 I’m your UdyamSetu Saathi. Ask me about business ideas, market conditions, loans, schemes or your next steps.' }

function normalizeHistory(data) {
  const rows = Array.isArray(data?.messages) ? data.messages : Array.isArray(data) ? data : []
  return rows.filter((item) => item?.role && item?.content).map((item) => ({ role: item.role, content: String(item.content) }))
}

export default function AIAssistant() {
  const { t } = useLanguage()
  const [messages, setMessages] = useState([welcome])
  const [conversationId, setConversationId] = useState(() => window.localStorage.getItem('udyamsetu-conversation-id'))
  const [locationText, setLocationText] = useState(() => window.localStorage.getItem('udyamsetu-location-text') || '')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const stored = window.localStorage.getItem('udyamsetu-conversation-id')
    if (!stored) return
    getChatHistory(stored).then((data) => {
      const history = normalizeHistory(data)
      if (history.length) setMessages(history)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (locationText) return
    getLatestUserLocation(getUserId()).then((data) => {
      if (data?.estimated_address) {
        setLocationText(data.estimated_address)
        window.localStorage.setItem('udyamsetu-location-text', data.estimated_address)
      }
    }).catch(() => {})
  }, [locationText])

  const send = async (text) => {
    if (sending) return
    setError('')
    setMessages((current) => [...current, { role: 'user', content: text }])
    setSending(true)
    try {
      const data = await chat(text, conversationId, getUserId(), locationText || null)
      const nextId = data?.conversation_id || conversationId
      if (nextId) {
        setConversationId(nextId)
        window.localStorage.setItem('udyamsetu-conversation-id', nextId)
      }
      setMessages((current) => [...current, { role: 'assistant', content: data?.answer || data?.response || 'I could not prepare an answer right now.' }])
    } catch (requestError) {
      setMessages((current) => current.slice(0, -1))
      setError(friendlyError(requestError, 'I could not reach the assistant. Please try again.'))
    } finally {
      setSending(false)
    }
  }

  const resolveLocation = (result) => {
    const address = result?.estimated_address
    if (!address) return
    setLocationText(address)
    window.localStorage.setItem('udyamsetu-location-text', address)
  }

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader title={t('assistant', 'title')} subtitle={t('assistant', 'subtitle')} />
      <div className="mt-8 grid gap-5 lg:grid-cols-[1fr_300px]">
        <div className="soft-card p-4 sm:p-5">
          <ChatMessageList messages={messages} loading={sending} />
          {error && <div role="alert" className="mt-3 rounded-xl bg-red-50 p-3 text-xs text-red-700">{error}</div>}
          <div className="mt-4"><ChatInput onSend={send} disabled={sending} /></div>
        </div>
        <div className="grid gap-5">
          <AssistantPanel />
          <div className="soft-card p-5">
            <CurrentLocationButton onResolved={resolveLocation} />
            {locationText && <div className="mt-3 rounded-xl bg-[#f2f7ee] p-3 text-xs text-neutral-600"><span className="font-semibold text-neutral-900">Current area:</span> {locationText}</div>}
          </div>
          <div className="soft-card p-5"><SuggestedQuestions onSelect={send} /></div>
        </div>
      </div>
    </div>
  )
}
