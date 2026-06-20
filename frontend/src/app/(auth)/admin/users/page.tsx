"use client"
import { useState, useEffect } from "react"
import { Search, Plus, Shield, Mail, Phone, Pencil, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"

export default function AdminUsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ email: "", first_name: "", last_name: "", matricule: "", role: "VIEWER", phone: "", department: "", password: "" })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetchUsers = () => {
    setLoading(true)
    Promise.all([
      fetch(API + "/rbac/users/ADMIN/", { headers }).then(r => r.json()),
      fetch(API + "/rbac/users/MANAGER/", { headers }).then(r => r.json()),
      fetch(API + "/rbac/users/SUPERVISOR/", { headers }).then(r => r.json()),
      fetch(API + "/rbac/users/OPERATOR/", { headers }).then(r => r.json()),
      fetch(API + "/rbac/users/VIEWER/", { headers }).then(r => r.json()),
      fetch(API + "/rbac/users/AUDITOR/", { headers }).then(r => r.json()),
    ]).then(results => {
      const all = results.flatMap(r => (r.data?.users || r.data || []).filter(Boolean))
      setUsers(all)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(() => { fetchUsers() }, [])

  const createUser = async () => {
    await fetch(API + "/auth/register/", { method: "POST", headers, body: JSON.stringify({ ...form, password_confirm: form.password }) })
    setShow(false)
    fetchUsers()
  }

  const roleColors = { ADMIN: "bg-red-100 text-red-700", MANAGER: "bg-blue-100 text-blue-700", SUPERVISOR: "bg-purple-100 text-purple-700", OPERATOR: "bg-green-100 text-green-700", VIEWER: "bg-gray-100 text-gray-700", AUDITOR: "bg-yellow-100 text-yellow-700" }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Utilisateurs</h1><p className="text-sm text-gray-500">{users.length} utilisateur(s)</p></div>
        <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Ajouter</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Nom</th><th className="text-left px-6 py-3">Email</th><th className="text-center px-6 py-3">Rôle</th><th className="text-left px-6 py-3">Téléphone</th><th className="text-center px-6 py-3">Statut</th></tr></thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-b hover:bg-gray-50/30">
                <td className="px-6 py-4"><div className="flex items-center gap-3"><div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center font-bold text-emerald-600 text-xs">{(u.first_name||"")[0]}{(u.last_name||"")[0]}</div><div><p className="font-medium">{u.first_name} {u.last_name}</p><p className="text-xs text-gray-400">{u.matricule}</p></div></div></td>
                <td className="px-6 py-4 text-gray-500">{u.email}</td>
                <td className="px-6 py-4 text-center"><span className={"px-2.5 py-1 rounded-full text-xs font-medium " + (roleColors[u.role] || "")}>{u.role}</span></td>
                <td className="px-6 py-4 text-gray-500">{u.phone || "-"}</td>
                <td className="px-6 py-4 text-center"><span className="inline-block w-2 h-2 rounded-full bg-green-500"></span> Actif</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Modal open={show} onClose={() => setShow(false)} title="Nouvel utilisateur">
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} placeholder="Prénom" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} placeholder="Nom" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <input value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="Email" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.matricule} onChange={e => setForm({...form, matricule: e.target.value})} placeholder="Matricule" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} placeholder="Téléphone" className="w-full p-2.5 border rounded-xl text-sm" />
          <select value={form.role} onChange={e => setForm({...form, role: e.target.value})} className="w-full p-2.5 border rounded-xl text-sm">
            <option value="ADMIN">Administrateur</option><option value="MANAGER">Gestionnaire</option><option value="SUPERVISOR">Superviseur</option><option value="OPERATOR">Opérateur</option><option value="VIEWER">Lecteur</option><option value="AUDITOR">Auditeur</option>
          </select>
          <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} placeholder="Mot de passe" className="w-full p-2.5 border rounded-xl text-sm" />
          <button onClick={createUser} className="w-full py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer l'utilisateur</button>
        </div>
      </Modal>
    </div>
  )
}