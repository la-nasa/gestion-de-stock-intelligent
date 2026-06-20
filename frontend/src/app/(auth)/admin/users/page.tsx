"use client"
import { useState, useEffect } from "react"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"

export default function UsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  useEffect(() => {
    fetch(API + "/rbac/users/ADMIN/", { headers: { Authorization: "Bearer " + token } }).then(r => r.json()).then(d => { setUsers(d.data?.users || d.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])
  if (loading) return <Loading />
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Utilisateurs</h1>
      <div className="bg-white rounded-2xl shadow-sm border p-6">
        <table className="w-full text-sm"><thead><tr><th className="text-left py-2">Nom</th><th className="text-left py-2">Email</th><th className="text-left py-2">Rôle</th></tr></thead>
          <tbody>{users.map(u => <tr key={u.id} className="border-t"><td className="py-2">{u.full_name || u.email}</td><td className="py-2 text-gray-500">{u.email}</td><td className="py-2">{u.role}</td></tr>)}</tbody></table>
      </div>
    </div>
  )
}
