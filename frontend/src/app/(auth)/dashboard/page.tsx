"use client"
import { useState, useEffect } from "react"
import { Package, DollarSign, ShoppingCart, AlertTriangle, Download } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { Authorization: "Bearer " + token }

  useEffect(() => {
    fetch(API + "/dashboard/", { headers }).then(r => r.json()).then(d => { if (d.success) setData(d.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleExport = () => {
    const k = data?.kpis || {}
    const csv = "Indicateur,Valeur\nProduits," + (k.totalProducts||0) + "\nValeur stock," + (k.stockValue||0) + "\nCommandes," + (k.pendingOrders||0) + "\nAlertes," + (k.lowStockItems||0)
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "dashboard.csv"; a.click()
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  const kpis = data?.kpis || {}
  const stats = [
    { title: "Produits", value: kpis.totalProducts || 0, icon: Package, color: "from-emerald-500 to-teal-500" },
    { title: "Valeur stock", value: (kpis.stockValue || 0).toLocaleString() + " XAF", icon: DollarSign, color: "from-blue-500 to-indigo-500" },
    { title: "Commandes", value: kpis.pendingOrders || 0, icon: ShoppingCart, color: "from-amber-500 to-orange-500" },
    { title: "Alertes", value: kpis.lowStockItems || 0, icon: AlertTriangle, color: "from-rose-500 to-red-500" },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Tableau de bord</h1></div>
        <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {stats.map((s, i) => {
          const Icon = s.icon
          return (
            <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <div className={"p-2.5 rounded-xl bg-gradient-to-br " + s.color + " w-fit mb-3"}><Icon size={18} className="text-white" /></div>
              <p className="text-2xl font-bold text-gray-800">{s.value}</p>
              <p className="text-sm text-gray-500">{s.title}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
