"use client"
import { useState, useEffect } from "react"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"

export default function RolesPage() {
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  useEffect(() => {
    fetch(API + "/rbac/roles/", { headers: { Authorization: "Bearer " + token } }).then(r => r.json()).then(d => { setRoles(d.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])
  if (loading) return <Loading />
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Rôles</h1>
      <div className="grid grid-cols-3 gap-4">
        {roles.map(r => <div key={r.id} className="bg-white rounded-2xl p-5 shadow-sm border"><h3 className="font-semibold">{r.name}</h3><p className="text-sm text-gray-500">{r.code} - Niv.{r.level}</p><p className="text-xs text-gray-400">{r.users_count} utilisateurs</p></div>)}
      </div>
    </div>
  )
}
