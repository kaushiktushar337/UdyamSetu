import { useMemo, useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import ChatMessageList from '../components/assistant/ChatMessageList'
import SuggestedQuestions from '../components/assistant/SuggestedQuestions'
import ChatInput from '../components/assistant/ChatInput'
import AssistantPanel from '../components/assistant/AssistantPanel'
import { faq } from '../data/faq'
import { useLanguage } from '../context/LanguageContext'

const initialMessages = [
  { role: 'assistant', content: 'Namaste! 👋 Main aapka UdyamSetu Saathi hoon. Aap mujhe business idea, loan, schemes ya market ke baare mein pooch sakte hain.' },
  { role: 'user', content: 'Main apna dairy business shuru karna chahta hoon. Kya scheme mere liye sahi rahegi?' },
  { role: 'assistant', content: 'Aapke project cost aur available margin money ke basis par scheme recommend ki ja sakti hai. Aap calculator mein details bhar dein, main result ko simple language mein explain kar dunga.' },
]

export default function AIAssistant() {
  const [messages, setMessages] = useState(initialMessages)
    const { t } = useLanguage()

  const answerFor = useMemo(() => {
    return (question) => {
      const match = faq.find((item) => item.question.toLowerCase() === question.toLowerCase())
      return match?.answer ?? 'Main is prototype mein scheme rules, indicative calculations aur business guidance explain kar sakta hoon. Official approval ke liye authorized agency ki verification zaroori hai.'
    }
  }, [])

  const send = (text) => {
    setMessages((current) => [
      ...current,
      { role: 'user', content: text },
      { role: 'assistant', content: answerFor(text) },
    ])
  }

  return (
    <div className="page-container py-12 sm:py-16">
      <PageHeader
          title={t('assistant', 'title')}
          subtitle={t('assistant', 'subtitle')}
      />

      <div className="mt-8 grid gap-5 lg:grid-cols-[1fr_300px]">
        <div className="soft-card p-4 sm:p-5">
          <ChatMessageList messages={messages} />
          <div className="mt-4">
            <ChatInput onSend={send} />
          </div>
        </div>

        <div className="grid gap-5">
          <AssistantPanel />
          <div className="soft-card p-5">
            <SuggestedQuestions onSelect={send} />
          </div>
        </div>
      </div>
    </div>
  )
}
