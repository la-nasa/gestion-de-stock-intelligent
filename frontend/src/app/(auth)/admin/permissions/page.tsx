"use client"
import { useState, useEffect } from "react"
import { Shield, Key, Check, X } from "lucide-react"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const T = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + T(), ...m })

export default function PermissionsPage() {
  const [roles, setRoles] = useState([])
  const [permissions, setPermissions] = useState([])
  const [selectedRole, setSelectedRole] = useState("")
  const [rolePerms, setRolePerms] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(API + "/rbac/roles/", { headers: H() }).then(r => r.json()),
      fetch(API + "/rbac/permissions/", { headers: H() }).then(r => r.json())
    ]).then(([rd, pd]) => {
      setRoles(rd?.data || rd || [])
      setPermissions(pd?.data || pd || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (selectedRole) {
      fetch(API + "/rbac/roles/" + selectedRole + "/permissions/", { headers: H() })
        .then(r => r.json()).then(d => setRolePerms(d?.data || d || [])).catch(() => setRolePerms([]))
    }
  }, [selectedRole])

  const togglePerm = async (permCode) => {
    const has = rolePerms.some(rp => rp.permission?.code === permCode || rp.permission_code === permCode)
    if (has) {
      await fetch(API + "/rbac/roles/" + selectedRole + "/permissions/" + permCode + "/", { method: "DELETE", headers: H() })
    } else {
      await fetch(API + "/rbac/roles/" + selectedRole + "/permissions/", { method: "POST", headers: H(), body: JSON.stringify({ permission_code: permCode }) })
    }
    // Rafraîchir
    const r = await fetch(API + "/rbac/roles/" + selectedRole + "/permissions/", { headers: H() })
    const d = await r.json()
    setRolePerms(d?.data || d || [])
  }

  if (loading) return <Loading />

  const modules = [...new Set(permissions.map(p => p.module))]

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-800">Permissions par rôle</h1><p className="text-sm text-gray-500">Gérez les permissions de chaque rôle</p></div>

      <div className="bg-white rounded-2xl shadow-sm border p-6">
        <label className="text-sm font-medium text-gray-700 mb-2 block">Sélectionner un rôle</label>
        <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)} className="w-full md:w-64 p-2.5 border rounded-xl text-sm mb-6">
          <option value="">-- Choisir --</option>
          {roles.map(r => <option key={r.code} value={r.code}>{r.name} ({r.code})</option>)}
        </select>

        {selectedRole && (
          <div className="space-y-6">
            {modules.map(mod => (
              <div key={mod}>
                <h3 className="font-semibold text-gray-700 mb-3 uppercase text-xs tracking-wider">{mod}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {permissions.filter(p => p.module === mod).map(p => {
                    const has = rolePerms.some(rp => (rp.permission?.code || rp.permission_code) === p.code)
                    return (
                      <button key={p.code} onClick={() => togglePerm(p.code)}
                        className={"flex items-center justify-between p-3 rounded-xl border text-sm transition-all " + (has ? "bg-emerald-50 border-emerald-200 text-emerald-700" : "bg-gray-50 border-gray-200 text-gray-500 hover:border-gray-300")}>
                        <span>{p.name}</span>
                        {has ? <Check size={16} className="text-emerald-500" /> : <X size={16} className="text-gray-300" />}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}