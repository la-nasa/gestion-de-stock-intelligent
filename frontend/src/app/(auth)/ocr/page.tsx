"use client"
import { useState, useEffect } from "react"
import { Search } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function Page() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  

  if (loading) return <div className="p-8 text-gray-400">Chargement...</div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-800">OCR Factures</h1><p className="text-sm text-gray-500">{data.length} élément(s)</p></div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        {data.length === 0 ? <p className="text-gray-400 text-center py-8">Aucune donnée</p> : <pre className="text-xs">{JSON.stringify(data.slice(0, 5), null, 2)}</pre>}
      </div>
    </div>
  )
}