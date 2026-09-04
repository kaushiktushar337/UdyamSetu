const questions = [
  'Kaunsa scheme mere liye sahi rahega?',
  'Loan ke liye kya documents chahiye?',
  'Dairy business me kitni kamai hai?',
  'Repayment kaise karna hoga?',
  'Kya mahilaon ke liye alag scheme hai?',
]

export default function SuggestedQuestions({ onSelect }) {
  return (
    <div>
      <div className="text-xs font-semibold text-neutral-900">Popular Questions</div>
      <div className="mt-3 grid gap-2">
        {questions.map((question) => (
          <button
            key={question}
            onClick={() => onSelect(question)}
            className="rounded-xl border border-neutral-100 bg-white px-3 py-3 text-left text-[11px] leading-4 text-neutral-600 hover:border-udyam-200 hover:bg-udyam-50"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}
