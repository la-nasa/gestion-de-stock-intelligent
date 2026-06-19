"use client"
import { Search, Plus } from "lucide-react"

export default function Page() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Paramètres</h1><p className="text-sm text-gray-500 mt-1">Gestion des paramètres</p></div>
        <button className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg transition-all"><Plus size={16} /> Nouveau</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="relative max-w-sm mb-6">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20" />
        </div>
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg font-medium">Page Paramètres</p>
          <p className="text-sm mt-1">Contenu à venir</p>
        </div>
      </div>
    </div>
  )
}