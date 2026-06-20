"use client"
import { useState, useEffect } from "react"
import { Search, Plus, Shield, Pencil, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const T = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + T(), ...m })

export default function AdminUsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ email: "", first_name: "", last_name: "", matricule: "", role: "VIEWER", phone: "", password: "" })

  const fetchData = () => {
    setLoading(true)
    const roles = ["ADMIN","MANAGER","SUPERVISOR","OPERATOR","VIEWER","AUDITOR"]
    Promise.all(roles.map(r => fetch(API + "/rbac/users/" + r + "/", { headers: H() }).then(r => r.json()).catch(() => ({ data: { users: [] } }))))
      .then(results => {
        const all = results.flatMap(r => {
          const d = r?.data?.users || r?.data || []
          return Array.isArray(d) ? d : []
        })
        setUsers(all)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const openCreate = () => { setEdit(null); setForm({ email: "", first_name: "", last_name: "", matricule: "", role: "VIEWER", phone: "", password: "" }); setShow(true) }
  const openEdit = (u) => { setEdit(u.id); setForm({ email: u.email||"", first_name: u.first_name||"", last_name: u.last_name||"", matricule: u.matricule||"", role: u.role||"VIEWER", phone: u.phone||"", password: "" }); setShow(true) }

  const save = async () => {
    if (!form.email || !form.first_name || !form.last_name || !form.matricule) return alert("Champs obligatoires")
    if (edit) {
      await fetch(API + "/auth/profile/", { method: "PATCH", headers: H(), body: JSON.stringify(form) })
    } else {
      if (!form.password) return alert("Mot de passe obligatoire")
      await fetch(API + "/auth/register/", { method: "POST", headers: H(), body: JSON.stringify({...form, password_confirm: form.password}) })
    }
    setShow(false); fetchData()
  }

  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/products/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const roleColors = { ADMIN: "bg-red-100 text-red-700", MANAGER: "bg-blue-100 text-blue-700", SUPERVISOR: "bg-purple-100 text-purple-700", OPERATOR: "bg-green-100 text-green-700", VIEWER: "bg-gray-100 text-gray-700", AUDITOR: "bg-yellow-100 text-yellow-700" }

  if (loading) return <Loading />
  const f = users.filter(u => (u.email||"").toLowerCase().includes("") || (u.first_name||"").toLowerCase().includes(""))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Utilisateurs</h1><p className="text-sm text-gray-500">{users.length} utilisateur(s)</p></div>
        <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Ajouter</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Nom</th><th className="text-left px-6 py-3">Email</th><th className="text-center px-6 py-3">Rôle</th><th className="text-left px-6 py-3">Téléphone</th><th className="text-center px-6 py-3">Actions</th></tr></thead>
        <tbody>{f.map(u => (<tr key={u.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4"><div className="flex items-center gap-3"><div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center font-bold text-emerald-600 text-xs">{(u.first_name||"")[0]}{(u.last_name||"")[0]}</div><div><p className="font-medium">{u.first_name} {u.last_name}</p><p className="text-xs text-gray-400">{u.matricule}</p></div></div></td><td className="px-6 py-4 text-gray-500">{u.email}</td><td className="px-6 py-4 text-center"><span className={"px-2.5 py-1 rounded-full text-xs font-medium "+(roleColors[u.role]||"")}>{u.role}</span></td><td className="px-6 py-4 text-gray-500">{u.phone||"-"}</td><td className="px-6 py-4"><div className="flex justify-center gap-1"><button onClick={() => openEdit(u)} className="p-1 hover:bg-gray-100 rounded"><Pencil size={14} /></button><button onClick={() => del(u.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></div></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier" : "Nouvel utilisateur"}>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} placeholder="Prénom *" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} placeholder="Nom *" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <input value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="Email *" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.matricule} onChange={e => setForm({...form, matricule: e.target.value})} placeholder="Matricule *" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} placeholder="Téléphone" className="w-full p-2.5 border rounded-xl text-sm" />
          <select value={form.role} onChange={e => setForm({...form, role: e.target.value})} className="w-full p-2.5 border rounded-xl text-sm">
            <option value="ADMIN">Administrateur</option><option value="MANAGER">Gestionnaire</option><option value="SUPERVISOR">Superviseur</option><option value="OPERATOR">Opérateur</option><option value="VIEWER">Lecteur</option><option value="AUDITOR">Auditeur</option>
          </select>
          {!edit && <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} placeholder="Mot de passe *" className="w-full p-2.5 border rounded-xl text-sm" />}
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">{edit ? "Modifier" : "Créer"}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}