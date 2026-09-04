export default function SchemeTabs({ active, onChange, schemes }) {
  return (
    <div className="inline-flex rounded-xl bg-udyam-50 p-1">
      {schemes.map((scheme) => (
        <button
          key={scheme.id}
          onClick={() => onChange(scheme.id)}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            active === scheme.id ? 'bg-udyam-600 text-white shadow-sm' : 'text-udyam-700 hover:bg-white'
          }`}
        >
          {scheme.name}
        </button>
      ))}
    </div>
  )
}
