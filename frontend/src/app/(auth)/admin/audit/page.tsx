"use client"
import { useState, useEffect } from "react"
import { Download, Search, Calendar, FileSearch } from "lucide-react"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ Authorization: "Bearer " + token(), ...m })

export default function AuditPage() {
  const [logs, setLogs] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(API + "/movements/", { headers: H() }).then(r => r.json()).then(d => {
      const items = (d?.data?.results || d.data || []).map(m => ({
        id: m.id, user: m.performed_by_name || "Système", action: m.movement_type === "ENTRY" ? "Entrée" : m.movement_type === "OUTPUT" ? "Sortie" : m.movement_type,
        module: "Stock", ip: "192.168.1.1", date: new Date(m.created_at).toLocaleString("fr-FR"), details: m.product_name + " x" + m.quantity
      }))
      setLogs(items); setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const exp = () => {
    const csv = "Date,Utilisateur,Action,Module,Détails\n" + logs.map(l => [l.date,l.user,l.action,l.module,l.details].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "audit.csv"; a.click()
  }

  if (loading) return <Loading />
  const f = logs.filter(l => (l.user||"").toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Logs d'audit</h1><p className="text-sm text-gray-500">{logs.length} actions</p></div>
        <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Date</th><th className="text-left px-6 py-3">Utilisateur</th><th className="text-left px-6 py-3">Action</th><th className="text-left px-6 py-3">Module</th><th className="text-left px-6 py-3">Détails</th></tr></thead>
        <tbody>{f.map(l => (<tr key={l.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 text-gray-500 text-xs"><Calendar size={12} className="inline mr-1" />{l.date}</td><td className="px-6 py-4 font-medium">{l.user}</td><td className="px-6 py-4">{l.action}</td><td className="px-6 py-4"><span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">{l.module}</span></td><td className="px-6 py-4 text-gray-500">{l.details}</td></tr>))}</tbody></table>
      </div>
    </div>
  )
}