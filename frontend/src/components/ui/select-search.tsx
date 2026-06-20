"use client"
import { useState, useEffect } from "react"

export function SelectSearch({ apiUrl, value, onChange, placeholder, labelField, valueField }) {
  const [options, setOptions] = useState([])
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""

  useEffect(() => {
    if (apiUrl) {
      fetch(apiUrl, { headers: { Authorization: "Bearer " + token } })
        .then(r => r.json())
        .then(d => {
          const items = d.data?.results || d.data || []
          setOptions(items)
        })
        .catch(() => {})
    }
  }, [apiUrl])

  const filtered = options.filter(o => {
    const label = (labelField ? o[labelField] : o.name) || ""
    return label.toLowerCase().includes(search.toLowerCase())
  })

  const selected = options.find(o => (valueField ? o[valueField] : o.id) === value)
  const displayName = selected ? (labelField ? selected[labelField] : selected.name) : (value || placeholder || "Sélectionner...")

  return (
    <div className="relative">
      <button type="button" onClick={() => setOpen(!open)} className="w-full p-2.5 border border-gray-200 rounded-xl text-sm text-left bg-white hover:border-emerald-400 transition-colors">
        <span className={selected ? "text-gray-800" : "text-gray-400"}>{displayName}</span>
      </button>
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full p-2 border-b text-sm" autoFocus />
          {filtered.map(o => (
            <div key={valueField ? o[valueField] : o.id} onClick={() => { onChange(valueField ? o[valueField] : o.id); setOpen(false) }} className="px-3 py-2 text-sm hover:bg-emerald-50 cursor-pointer">
              {labelField ? o[labelField] : o.name}
            </div>
          ))}
          {filtered.length === 0 && <div className="px-3 py-2 text-sm text-gray-400">Aucun résultat</div>}
        </div>
      )}
    </div>
  )
}
