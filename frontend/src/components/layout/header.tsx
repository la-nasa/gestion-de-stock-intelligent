"use client"
import React from "react"
import { Bell, Search, Sun, Moon } from "lucide-react"

export function Header() {
  const [dark, setDark] = React.useState(false)
  return (
    <header className="sticky top-0 z-30 h-16 bg-white/90 backdrop-blur-md border-b border-gray-100 flex items-center gap-4 px-6 shadow-sm">
      <div className="flex-1 max-w-lg">
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 focus:bg-white transition-all" />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
          <Bell size={18} className="text-gray-500" />
          <span className="absolute top-1.5 right-1.5 h-4 w-4 bg-emerald-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">3</span>
        </button>
        <button onClick={() => setDark(!dark)} className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
          {dark ? <Sun size={18} className="text-gray-500" /> : <Moon size={18} className="text-gray-500" />}
        </button>
      </div>
    </header>
  )
}