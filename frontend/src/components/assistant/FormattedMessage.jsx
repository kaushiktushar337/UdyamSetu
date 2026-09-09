function renderInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-semibold text-neutral-900">{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={index} className="rounded bg-neutral-100 px-1 py-0.5 text-[11px]">{part.slice(1, -1)}</code>
    }
    return <span key={index}>{part}</span>
  })
}

export default function FormattedMessage({ content }) {
  const lines = String(content || '').replace(/\r/g, '').split('\n')
  const blocks = []
  let list = null

  const flushList = () => {
    if (!list) return
    const type = list.type
    const items = list.items
    blocks.push(
      type === 'ul'
        ? <ul key={`ul-${blocks.length}`} className="my-2 list-disc space-y-1 pl-5">{items}</ul>
        : <ol key={`ol-${blocks.length}`} className="my-2 list-decimal space-y-1 pl-5">{items}</ol>
    )
    list = null
  }

  lines.forEach((raw, index) => {
    const line = raw.trim()
    if (!line) {
      flushList()
      return
    }

    const bullet = line.match(/^[-*]\s+(.+)/)
    const numbered = line.match(/^\d+[.)]\s+(.+)/)
    const heading = line.match(/^#{1,3}\s+(.+)/)

    if (bullet || numbered) {
      const type = bullet ? 'ul' : 'ol'
      if (!list || list.type !== type) {
        flushList()
        list = { type, items: [] }
      }
      list.items.push(<li key={`${index}-${list.items.length}`}>{renderInline((bullet || numbered)[1])}</li>)
      return
    }

    flushList()
    if (heading) {
      blocks.push(<h4 key={`h-${index}`} className="mt-3 mb-1 text-xs font-semibold text-neutral-900">{renderInline(heading[1])}</h4>)
      return
    }
    blocks.push(<p key={`p-${index}`} className="my-1.5">{renderInline(line)}</p>)
  })

  flushList()
  return <div className="chat-formatted text-[13px] leading-5">{blocks}</div>
}
