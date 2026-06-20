"use client"
import { useState, useEffect } from "react"
import { Search, Download, Package, TrendingUp, AlertTriangle } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function StocksPage() {
  const [stocks, setStocks] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { Authorization: "Bearer " + token }

  useEffect(() => {
    fetch(API + "/stocks/", { headers }).then(r => r.json()).then(d => { setStocks(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleExport = () => {
    const csv = "Produit,Référence,Entrepôt,Quantité,Disponible,Prix,Valeur\n" + stocks.map(s => [s.product_name, s.product_reference, s.warehouse_name, s.quantity, s.available_quantity, s.unit_price, s.quantity * s.unit_price].join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "stocks.csv"; a.click()
  }

  const totalValue = stocks.reduce((s, x) => s + (x.quantity || 0) * (x.unit_price || 0), 0)
  const filtered = stocks.filter(s => (s.product_name || "").toLowerCase().includes(search.toLowerCase()))

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Stocks</h1><p className="text-sm text-gray-500">Valeur totale : {totalValue.toLocaleString()} XAF</p></div>
        <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Produit</th><th className="text-left px-6 py-3">Entrepôt</th><th className="text-center px-6 py-3">Qté</th><th className="text-right px-6 py-3">Prix</th><th className="text-right px-6 py-3">Valeur</th></tr></thead>
          <tbody>{filtered.map(s => (<tr key={s.id} className="border-b border-gray-50"><td className="px-6 py-4"><p className="font-medium">{s.product_name}</p><p className="text-xs text-gray-400">{s.product_reference}</p></td><td className="px-6 py-4"><span className="px-2 py-1 rounded-full text-xs bg-blue-50 text-blue-700">{s.warehouse_name}</span></td><td className="px-6 py-4 text-center font-semibold">{s.quantity}</td><td className="px-6 py-4 text-right">{s.unit_price?.toLocaleString()}</td><td className="px-6 py-4 text-right font-semibold">{((s.quantity||0)*(s.unit_price||0)).toLocaleString()}</td></tr>))}</tbody></table>
      </div>
    </div>
  )
}
