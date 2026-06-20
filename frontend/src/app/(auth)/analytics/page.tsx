"use client"
import { useState, useEffect } from "react"
import { BarChart3, TrendingUp, DollarSign, Package, TrendingDown } from "lucide-react"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"

export default function AnalyticsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { Authorization: "Bearer " + token }

  useEffect(() => {
    fetch(API + "/dashboard/", { headers }).then(r => r.json()).then(d => {
      if (d.success) setData(d.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <Loading />

  const kpis = data?.kpis || {}
  const monthly = data?.monthlyConsumption || []
  const byCategory = data?.stockByCategory || []

  const stats = [
    { label: "Valeur stock", value: (kpis.stockValue || 0).toLocaleString() + " XAF", icon: DollarSign, color: "#0d9488", change: "+8.2%" },
    { label: "Rotation stock", value: "4.2x", icon: TrendingUp, color: "#2563eb", change: "+0.3x" },
    { label: "Produits actifs", value: kpis.totalProducts || 0, icon: Package, color: "#7c3aed", change: "+12" },
    { label: "Commandes mois", value: kpis.pendingOrders || 0, icon: BarChart3, color: "#ca8a04", change: "-5" },
  ]

  const maxVal = Math.max(...monthly.map(m => m.value || 0), 1)

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-800">Analytiques</h1><p className="text-sm text-gray-500">Statistiques et analyses avancées</p></div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {stats.map((s, i) => {
          const Icon = s.icon
          return (
            <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl" style={{background: s.color + "15"}}><Icon size={20} style={{color: s.color}} /></div>
                <span className="text-xs font-medium text-emerald-600">{s.change}</span>
              </div>
              <p className="text-2xl font-bold text-gray-800">{s.value}</p>
              <p className="text-sm text-gray-500">{s.label}</p>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <h3 className="font-semibold text-gray-800 mb-4">Consommation mensuelle (XAF)</h3>
          <div className="h-64 flex items-end gap-2">
            {monthly.map((m, i) => {
              const h = maxVal > 0 ? (m.value / maxVal) * 100 : 0
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <span className="text-[10px] text-gray-400">{m.value?.toLocaleString()}</span>
                  <div className="w-full rounded-t-md bg-gradient-to-t from-emerald-500 to-teal-400 transition-all hover:opacity-80" style={{height: h + "%"}}></div>
                  <span className="text-[10px] text-gray-400">{m.month}</span>
                </div>
              )
            })}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <h3 className="font-semibold text-gray-800 mb-4">Valeur par catégorie</h3>
          {byCategory.length > 0 ? (
            <div className="space-y-3">
              {byCategory.map((c, i) => {
                const total = byCategory.reduce((s, x) => s + (x.value||0), 0)
                const pct = total > 0 ? Math.round((c.value / total) * 100) : 0
                const colors = ["#0d9488","#2563eb","#ca8a04","#7c3aed","#dc2626","#0891b2"]
                return (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1"><span className="text-gray-600">{c.name}</span><span className="font-medium">{c.value?.toLocaleString()} XAF ({pct}%)</span></div>
                    <div className="h-2 bg-gray-100 rounded-full"><div className="h-full rounded-full transition-all" style={{width: pct + "%", background: colors[i % colors.length]}}></div></div>
                  </div>
                )
              })}
            </div>
          ) : <p className="text-gray-400 text-center py-8">Aucune donnée</p>}
        </div>
      </div>
    </div>
  )
}