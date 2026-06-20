"use client"
import { useState, useEffect } from "react"
import { Shield, Key, Users } from "lucide-react"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"

export default function AdminRolesPage() {
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { Authorization: "Bearer " + token }

  useEffect(() => {
    fetch(API + "/rbac/roles/", { headers }).then(r => r.json()).then(d => {
      const data = d.data || []
      setRoles(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <Loading />

  const colors = ["#1a3a5c", "#0d9488", "#7c3aed", "#2563eb", "#ca8a04", "#dc2626"]
  const icons = [Shield, Shield, Shield, Shield, Shield, Shield]

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-800">Rôles & Permissions</h1><p className="text-sm text-gray-500">{roles.length} rôles configurés</p></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {roles.map((r, i) => {
          const Icon = icons[i % icons.length]
          return (
            <div key={r.id} className="bg-white rounded-2xl p-6 shadow-sm border hover:shadow-md transition-all">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 rounded-xl" style={{background: colors[i % colors.length] + "15"}}>
                  <Icon size={24} style={{color: colors[i % colors.length]}} />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-800">{r.name}</h3>
                  <p className="text-xs text-gray-400">{r.code}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-500">Niveau</span><span className="font-medium">{r.level}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Utilisateurs</span><span className="font-medium">{r.users_count || 0}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Permissions</span><span className="font-medium">{r.permissions_count || 0}</span></div>
              </div>
              <div className="mt-4 pt-4 border-t">
                <button className="text-xs text-emerald-600 hover:underline">Gérer les permissions →</button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}