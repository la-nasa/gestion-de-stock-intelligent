"use client"
import { useState, useEffect } from "react"
import { Plus, Download, ClipboardList } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function InventoriesPage() {
  const [inventories, setInventories] = useState([])
  const [loading, setLoading] = useState(true)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  useEffect(() => {
    fetch(API + "/inventories/", { headers }).then(r => r.json()).then(d => { setInventories(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleCreate = async () => {
    const warehouseId = prompt("ID de l'entrepôt (UUID) :")
    if (!warehouseId) return
    await fetch(API + "/inventories/", { method: "POST", headers, body: JSON.stringify({ warehouse_id: warehouseId, type: "FULL", description: "Inventaire manuel" }) })
    window.location.reload()
  }

  const handleExport = () => {
    const csv = "Référence,Entrepôt,Date,Articles,Écarts,Statut\n" + inventories.map(i => [i.reference, i.warehouse_name, i.start_date, i.counted_items + "/" + i.expected_items, i.differences, i.status].join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "inventaires.csv"; a.click()
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Inventaires</h1><p className="text-sm text-gray-500">{inventories.length} inventaire(s)</p></div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
          <button onClick={handleCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvel inventaire</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Référence</th><th className="text-left px-6 py-3">Entrepôt</th><th className="text-center px-6 py-3">Articles</th><th className="text-center px-6 py-3">Écarts</th><th className="text-center px-6 py-3">Statut</th></tr></thead>
          <tbody>{inventories.map(i => (<tr key={i.id} className="border-b border-gray-50"><td className="px-6 py-4 font-medium">{i.reference}</td><td className="px-6 py-4">{i.warehouse_name}</td><td className="px-6 py-4 text-center">{i.counted_items}/{i.expected_items}</td><td className="px-6 py-4 text-center"><span className={i.differences === 0 ? "text-emerald-600" : "text-red-600"}>{i.differences}</span></td><td className="px-6 py-4 text-center"><span className="px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-700">{i.status}</span></td></tr>))}</tbody></table>
      </div>
    </div>
  )
}
