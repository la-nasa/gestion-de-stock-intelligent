"use client"
import { Package, DollarSign, ShoppingCart, AlertTriangle, ArrowUpDown, Users, TrendingUp, TrendingDown } from "lucide-react"

const stats = [
  { title: "Produits en stock", value: "2 847", change: "+12.5%", trend: "up", icon: Package, color: "from-emerald-500 to-teal-500", bg: "bg-emerald-50" },
  { title: "Valeur du stock", value: "156.8M XAF", change: "+8.2%", trend: "up", icon: DollarSign, color: "from-blue-500 to-indigo-500", bg: "bg-blue-50" },
  { title: "Commandes en cours", value: "24", change: "-3.1%", trend: "down", icon: ShoppingCart, color: "from-amber-500 to-orange-500", bg: "bg-amber-50" },
  { title: "Produits en alerte", value: "18", change: "+5.5%", trend: "up", icon: AlertTriangle, color: "from-rose-500 to-red-500", bg: "bg-rose-50" },
  { title: "Transferts actifs", value: "7", change: "+2", trend: "up", icon: ArrowUpDown, color: "from-violet-500 to-purple-500", bg: "bg-violet-50" },
  { title: "Fournisseurs", value: "86", change: "+4", trend: "up", icon: Users, color: "from-cyan-500 to-sky-500", bg: "bg-cyan-50" },
]

const activities = [
  { action: "Entrée stock", product: "Ordinateurs Dell", qty: 50, user: "Jean Kouam", time: "Il y a 2h", color: "bg-emerald-100 text-emerald-700" },
  { action: "Sortie stock", product: "Papier A4", qty: 200, user: "Marie Ngo", time: "Il y a 3h", color: "bg-blue-100 text-blue-700" },
  { action: "Transfert", product: "Projecteurs Epson", qty: 5, user: "Paul Biya", time: "Il y a 5h", color: "bg-violet-100 text-violet-700" },
  { action: "Inventaire", product: "Salle informatique B", user: "Admin", time: "Il y a 1j", color: "bg-amber-100 text-amber-700" },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Tableau de bord</h1>
          <p className="text-sm text-gray-500 mt-1">Vue d'ensemble de votre gestion de stock</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 text-sm border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">Cette semaine</button>
          <button className="px-4 py-2 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg transition-all">Exporter</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {stats.map((s, i) => {
          const Icon = s.icon
          return (
            <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all cursor-pointer group">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-2.5 rounded-xl bg-gradient-to-br ${s.color} shadow-sm`}>
                  <Icon size={18} className="text-white" />
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${s.trend === "up" ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-600"}`}>
                  {s.trend === "up" ? <TrendingUp size={12} className="inline mr-0.5" /> : <TrendingDown size={12} className="inline mr-0.5" />}
                  {s.change}
                </span>
              </div>
              <p className="text-2xl font-bold text-gray-800">{s.value}</p>
              <p className="text-sm text-gray-500 mt-1">{s.title}</p>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-800 mb-4">Consommation mensuelle (XAF)</h3>
          <div className="h-64 flex items-end gap-2">
            {[65,78,52,91,88,73,95,82,68,89,94,77].map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
                <span className="text-[10px] text-gray-400 font-medium">{(h*25000).toLocaleString()}</span>
                <div className="w-full rounded-t-lg transition-all hover:opacity-80 cursor-pointer" 
                     style={{height: `${h}%`, background: "linear-gradient(180deg, #0d9488, #1e40af)"}}></div>
                <span className="text-[10px] text-gray-400">{["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"][i]}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-800 mb-4">Activités récentes</h3>
          <div className="space-y-3">
            {activities.map((a, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors">
                <div className={`p-2 rounded-lg ${a.color} text-xs font-medium shrink-0`}>{a.action}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">{a.product}</p>
                  <p className="text-xs text-gray-400">{a.qty ? `Qté: ${a.qty} • ` : ""}{a.user} • {a.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}