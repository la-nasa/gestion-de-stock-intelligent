"use client"
import { useState } from "react"
import { FileText, FileSpreadsheet, Download, Loader2 } from "lucide-react"

const API = "http://localhost:8000/api/v1"

const reportTypes = [
  { id: "stock_level", name: "Niveau de stock", icon: FileText, color: "border-emerald-200 bg-emerald-50 text-emerald-700" },
  { id: "movements", name: "Mouvements", icon: FileSpreadsheet, color: "border-blue-200 bg-blue-50 text-blue-700" },
  { id: "consumption", name: "Consommation", icon: FileText, color: "border-amber-200 bg-amber-50 text-amber-700" },
]

export default function ReportsPage() {
  const [type, setType] = useState("stock_level")
  const [format, setFormat] = useState("CSV")
  const [loading, setLoading] = useState(false)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const res = await fetch(API + "/reports/generate/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
        body: JSON.stringify({ type, format, filters: {} })
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a"); a.href = url; a.download = "rapport_" + type + "." + format.toLowerCase(); a.click()
        URL.revokeObjectURL(url)
      } else {
        const err = await res.json().catch(() => ({}))
        alert("Erreur: " + (err.message || "Génération impossible"))
      }
    } catch (e) { alert("Erreur: " + e.message) }
    setLoading(false)
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div><h1 className="text-2xl font-bold text-gray-800">Rapports</h1><p className="text-sm text-gray-500">Générez des rapports CSV/Excel</p></div>
      <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-6">
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-3">Type de rapport</p>
          <div className="grid grid-cols-2 gap-3">
            {reportTypes.map(r => (
              <button key={r.id} onClick={() => setType(r.id)} className={"flex items-center gap-3 p-4 rounded-xl border-2 transition-all " + (type === r.id ? r.color + " border-current" : "border-gray-100 hover:border-gray-200")}>
                <r.icon size={20} /><span className="font-medium text-sm">{r.name}</span>
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-3">Format</p>
          <div className="flex gap-3">
            {["CSV","EXCEL"].map(f => (
              <button key={f} onClick={() => setFormat(f)} className={"px-5 py-2.5 rounded-xl text-sm font-medium border-2 transition-all " + (format === f ? "border-emerald-500 bg-emerald-50 text-emerald-700" : "border-gray-100 hover:border-gray-200")}>{f}</button>
            ))}
          </div>
        </div>
        <button onClick={handleGenerate} disabled={loading} className="w-full py-3 text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg disabled:opacity-50">
          {loading ? <Loader2 size={18} className="inline animate-spin mr-2" /> : <Download size={18} className="inline mr-2" />}
          {loading ? "Génération..." : "Générer le rapport"}
        </button>
      </div>
    </div>
  )
}