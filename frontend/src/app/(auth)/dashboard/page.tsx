"use client"
import { useState, useEffect } from "react"
import { Search, Download } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function Page() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { Authorization: "Bearer " + token }

  useEffect(() => {
    fetch(API + "/dashboard/", { headers })
      .then(r => r.json())
      .then(d => {
        const items = d?.results || d?.data?.results || d?.data || []
        setData(Array.isArray(items) ? items : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = data.filter(item => JSON.stringify(item).toLowerCase().includes(search.toLowerCase()))
  const keys = filtered.length > 0 ? Object.keys(filtered[0]).slice(0, 6) : []

  const exportCSV = () => {
    if (filtered.length === 0) return
    const csv = keys.join(",") + "\n" + filtered.map(item => keys.map(k => item[k] ?? "").join(",")).join("\n")
    const a = document.createElement("a")
    a.href = URL.createObjectURL(new Blob(["\uFEFF" + csv]))
    a.download = "dashboard.csv"
    a.click()
  }

  if (loading) return <div className="flex justify-center h-64 items-center"><div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">dashboard</h1><p className="text-sm text-gray-500">{data.length} élément(s)</p></div>
        <button onClick={exportCSV} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <div className="overflow-x-auto">
          {filtered.length > 0 ? (
            <table className="w-full text-sm">
              <thead className="bg-gray-50"><tr>{keys.map(k => <th key={k} className="text-left px-4 py-2 font-semibold text-gray-600">{k}</th>)}</tr></thead>
              <tbody>{filtered.slice(0, 50).map((item, i) => <tr key={i} className="border-b hover:bg-gray-50/30">{keys.map(k => <td key={k} className="px-4 py-2 text-gray-700">{typeof item[k] === "object" ? JSON.stringify(item[k]) : String(item[k] ?? "")}</td>)}</tr>)}</tbody>
            </table>
          ) : <p className="text-gray-400 text-center py-12">Aucune donnée</p>}
        </div>
      </div>
    </div>
  )
}