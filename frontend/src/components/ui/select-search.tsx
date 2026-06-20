"use client"
import { useState, useEffect, useRef } from "react"

export function SelectSearch({ apiUrl, value, onChange, placeholder, labelField, valueField }) {
  const [options, setOptions] = useState([])
  const [search, setSearch] = useState("")
  const [open, setOpen] = useState(false)
  const [selectedLabel, setSelectedLabel] = useState("")
  const ref = useRef(null)
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""

  useEffect(() => {
    if (apiUrl) {
      fetch(apiUrl, { headers: { Authorization: "Bearer " + token } })
        .then(r => r.json())
        .then(d => {
          // CORRECTION: Accepter plusieurs formats de réponse
          const items = d?.data?.results || d?.data || d?.results || d || []
          const arr = Array.isArray(items) ? items : []
          setOptions(arr)
          // Trouver le label correspondant à la valeur actuelle
          if (value && arr.length > 0) {
            const found = arr.find(o => (valueField ? o[valueField] : o.id) === value)
            if (found) setSelectedLabel(labelField ? found[labelField] : (found.name || found.warehouse_name || ""))
          }
        })
        .catch(() => setOptions([]))
    }
  }, [apiUrl])

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const filtered = options.filter(o => {
    const label = (labelField ? o[labelField] : (o.name || o.warehouse_name || ""))
    return label && label.toLowerCase().includes(search.toLowerCase())
  })

  const handleSelect = (item) => {
    const val = valueField ? item[valueField] : item.id
    const label = labelField ? item[labelField] : (item.name || item.warehouse_name || "")
    onChange(val)
    setSelectedLabel(label)
    setOpen(false)
    setSearch("")
  }

  return (
    <div ref={ref} className="relative">
      <button type="button" onClick={() => setOpen(!open)} className="w-full p-2.5 border border-gray-200 rounded-xl text-sm text-left bg-white hover:border-emerald-400 transition-colors">
        <span className={selectedLabel ? "text-gray-800" : "text-gray-400"}>{selectedLabel || value || placeholder || "Sélectionner..."}</span>
      </button>
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full p-2 border-b text-sm" autoFocus onClick={e => e.stopPropagation()} />
          {filtered.length > 0 ? filtered.map(o => (
            <div key={valueField ? o[valueField] : o.id} onClick={() => handleSelect(o)} className="px-3 py-2 text-sm hover:bg-emerald-50 cursor-pointer">
              {labelField ? o[labelField] : (o.name || o.warehouse_name || o.id)}
            </div>
          )) : <div className="px-3 py-2 text-sm text-gray-400">Aucun résultat ({options.length} options)</div>}
        </div>
      )}
    </div>
  )
}
