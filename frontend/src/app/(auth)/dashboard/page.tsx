"use client"
import { useState, useEffect } from "react"
import { Package, DollarSign, ShoppingCart, AlertTriangle, ArrowUpDown, Users, Download } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from "recharts"

const API = "http://localhost:8000/api/v1"
const COLORS = ["#0d9488","#2563eb","#ca8a04","#7c3aed","#dc2626","#0891b2"]

export default function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""

  useEffect(() => {
    fetch(API + "/dashboard/", { headers: { Authorization: "Bearer " + token } })
      .then(r => r.json()).then(d => { if (d.success) setData(d.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-96"><div className="animate-spin h-10 w-10 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  const kpis = data?.kpis || {}
  const monthly = data?.monthlyConsumption || []
  const byCategory = data?.stockByCategory || []
  const activities = data?.recentActivities || []

  const stats = [
    { title: "Produits", value: kpis.totalProducts||0, icon: Package, color: "from-emerald-500 to-teal-500", bg: "bg-emerald-50" },
    { title: "Valeur stock", value: (kpis.stockValue||0).toLocaleString()+" XAF", icon: DollarSign, color: "from-blue-500 to-indigo-500", bg: "bg-blue-50" },
    { title: "Commandes", value: kpis.pendingOrders||0, icon: ShoppingCart, color: "from-amber-500 to-orange-500", bg: "bg-amber-50" },
    { title: "Alertes", value: kpis.lowStockItems||0, icon: AlertTriangle, color: "from-rose-500 to-red-500", bg: "bg-rose-50" },
    { title: "Transferts", value: kpis.activeTransfers||0, icon: ArrowUpDown, color: "from-violet-500 to-purple-500", bg: "bg-violet-50" },
    { title: "Fournisseurs", value: kpis.totalSuppliers||0, icon: Users, color: "from-cyan-500 to-sky-500", bg: "bg-cyan-50" },
  ]

  const exp = () => {
    const csv = "Indicateur,Valeur\n"+stats.map(s=>[s.title,s.value].join(",")).join("\n")
    const a=document.createElement("a"); a.href=URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download="dashboard.csv"; a.click()
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div><h1 className="text-2xl font-bold text-gray-800">Tableau de bord</h1><p className="text-sm text-gray-500">Vue d'ensemble IUC</p></div>
        <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((s,i)=>{const Icon=s.icon;return(
          <div key={i} className="bg-white rounded-2xl p-4 shadow-sm border hover:shadow-md transition-all">
            <div className={"p-2 rounded-xl bg-gradient-to-br "+s.color+" w-fit mb-3"}><Icon size={16} className="text-white"/></div>
            <p className="text-xl font-bold text-gray-800">{s.value}</p>
            <p className="text-xs text-gray-500">{s.title}</p>
          </div>
        )})}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <h3 className="font-semibold text-gray-800 mb-4">Consommation mensuelle (XAF)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{fontSize:12}} />
              <YAxis tick={{fontSize:12}} />
              <Tooltip formatter={v => [v.toLocaleString()+" XAF",""]} />
              <Bar dataKey="value" fill="#0d9488" radius={[4,4,0,0]} name="Consommation" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <h3 className="font-semibold text-gray-800 mb-4">Répartition par catégorie</h3>
          {byCategory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={byCategory} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({name,percent}) => name+" "+(percent*100).toFixed(0)+"%"}>
                  {byCategory.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Pie>
                <Tooltip formatter={v=>[v.toLocaleString()+" XAF",""]}/>
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-center py-12">Aucune donnée</p>}
        </div>
      </div>

      {activities.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border">
          <h3 className="font-semibold text-gray-800 mb-4">Activités récentes</h3>
          <div className="space-y-2">
            {activities.slice(0,8).map((a,i)=>(
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50">
                <span className="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-700 text-xs font-medium">{a.type||"Action"}</span>
                <span className="text-sm text-gray-700 truncate flex-1">{a.product}</span>
                <span className="text-xs text-gray-400">{a.user} • {a.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}