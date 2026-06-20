"use client"
import { Search } from "lucide-react"

export function SearchBar({ value, onChange, placeholder }) {
  return (
    <div className="relative max-w-sm">
      <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
      <input value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder || "Rechercher..."} className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 focus:bg-white transition-all" />
    </div>
  )
}
