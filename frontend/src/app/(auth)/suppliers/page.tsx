"use client"
import { useState } from "react"
import { Search, Plus, Building2, Phone, Mail, Star, MapPin } from "lucide-react"

const suppliers = [
  { name: "TechSupply Cameroun", contact: "M. Kamdem", email: "contact@techsupply.cm", phone: "+237 233 45 67 89", city: "Douala", rating: 5, cat: "Informatique" },
  { name: "BureauPlus SARL", contact: "Mme. Ndongo", email: "ventes@bureauplus.cm", phone: "+237 233 46 78 90", city: "Douala", rating: 4, cat: "Bureautique" },
  { name: "LaboEquip Afrique", contact: "Dr. Njoya", email: "info@laboequip.cm", phone: "+237 233 47 89 01", city: "Yaoundé", rating: 4, cat: "Laboratoire" },
  { name: "Africa Mobilier Pro", contact: "M. Kuete", email: "ventes@africamobilier.cm", phone: "+237 233 50 12 34", city: "Douala", rating: 4, cat: "Mobilier" },
  { name: "Papeterie Moderne", contact: "Mme. Foning", email: "contact@papeterie-moderne.cm", phone: "+237 233 49 01 23", city: "Douala", rating: 3, cat: "Papeterie" },
  { name: "SécuritéPlus SA", contact: "M. Ewane", email: "info@securiteplus.cm", phone: "+237 233 51 23 45", city: "Douala", rating: 5, cat: "Sécurité" },
]

export default function SuppliersPage() {
  const [search, setSearch] = useState("")
  const filtered = suppliers.filter(s => s.name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Fournisseurs</h1><p className="text-sm text-gray-500 mt-1">{suppliers.length} fournisseurs enregistrés</p></div>
        <button className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg transition-all"><Plus size={16} /> Nouveau fournisseur</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="relative max-w-sm mb-6">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((s, i) => (
            <div key={i} className="p-5 border border-gray-100 rounded-2xl hover:shadow-md hover:border-blue-200 transition-all cursor-pointer">
              <div className="flex items-start justify-between mb-3">
                <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-sm">
                  <Building2 size={18} className="text-white" />
                </div>
                <div className="flex items-center gap-0.5">
                  {Array.from({length: s.rating}).map((_,j) => <Star key={j} size={12} className="text-amber-400 fill-amber-400" />)}
                </div>
              </div>
              <h3 className="font-semibold text-gray-800 mb-1">{s.name}</h3>
              <p className="text-xs text-gray-400 mb-3">{s.cat} • {s.contact}</p>
              <div className="space-y-1.5 text-xs text-gray-500">
                <div className="flex items-center gap-2"><Phone size={12} /> {s.phone}</div>
                <div className="flex items-center gap-2"><Mail size={12} /> {s.email}</div>
                <div className="flex items-center gap-2"><MapPin size={12} /> {s.city}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}