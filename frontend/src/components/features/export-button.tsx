"use client"
import { Download } from "lucide-react"

export function ExportButton({ data, filename, headers }) {
  const handleExport = () => {
    if (!data || data.length === 0) return alert("Aucune donnée à exporter")
    const keys = headers || Object.keys(data[0])
    const csv = keys.join(",") + "\n" + data.map(row => keys.map(k => {
      const v = row[k] !== undefined ? row[k] : ""
      return typeof v === "string" && v.includes(",") ? '"' + v + '"' : v
    }).join(",")).join("\n")
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a"); a.href = url; a.download = filename || "export.csv"; a.click()
    URL.revokeObjectURL(url)
  }
  return <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"><Download size={16} /> Exporter</button>
}
