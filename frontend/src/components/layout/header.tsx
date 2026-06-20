"use client"
import React from "react"
import { Search, Sun, Moon, Menu } from "lucide-react"
import { NotificationBell } from "@/components/features/notification-bell"

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  const [dark, setDark] = React.useState(false)

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/90 backdrop-blur-md border-b border-gray-100 flex items-center gap-2 px-3 md:gap-4 md:px-6 shadow-sm">
      <button onClick={onMenuClick} className="lg:hidden p-2 rounded-xl hover:bg-gray-100 flex-shrink-0">
        <Menu size={20} className="text-gray-500" />
      </button>
      <div className="flex-1 max-w-lg">
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 focus:bg-white transition-all" />
        </div>
      </div>
      <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
        <NotificationBell />
        <button onClick={() => setDark(!dark)} className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
          {dark ? <Sun size={18} className="text-gray-500" /> : <Moon size={18} className="text-gray-500" />}
        </button>
      </div>
    </header>
  )
}
