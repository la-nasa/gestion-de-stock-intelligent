"use client"
import { useState, useEffect } from "react"
import { Shield, Plus, Pencil, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const T = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + T(), ...m })

export default function AdminRolesPage() {
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ name: "", code: "", description: "", level: 0 })

  const fetchData = () => {
    fetch(API + "/rbac/roles/", { headers: H() }).then(r => r.json()).then(d => {
      setRoles(d?.data || d || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const openCreate = () => { setEdit(null); setForm({ name: "", code: "", description: "", level: 0 }); setShow(true) }
  const openEdit = (r) => { setEdit(r.id); setForm({ name: r.name||"", code: r.code||"", description: r.description||"", level: r.level||0 }); setShow(true) }

  const save = async () => {
    if (!form.name || !form.code) return alert("Nom et code obligatoires")
    const url = edit ? API + "/rbac/roles/" + form.code + "/" : API + "/rbac/roles/"
    await fetch(url, { method: edit ? "PATCH" : "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }

  const del = async (code) => { if (confirm("Supprimer ?")) { await fetch(API + "/rbac/roles/" + code + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const colors = ["#0d9488","#2563eb","#7c3aed","#ca8a04","#dc2626","#0891b2"]
  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Rôles & Permissions</h1><p className="text-sm text-gray-500">{roles.length} rôles</p></div>
        <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-violet-500 to-purple-600 hover:shadow-lg"><Plus size={16} /> Nouveau rôle</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {roles.map((r, i) => (
          <div key={r.id} className="bg-white rounded-2xl p-6 shadow-sm border hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl" style={{background: colors[i%colors.length]+"15"}}><Shield size={24} style={{color: colors[i%colors.length]}} /></div>
              <div className="flex gap-1">
                <button onClick={() => openEdit(r)} className="p-1 hover:bg-gray-100 rounded"><Pencil size={14} /></button>
                {!r.is_system && <button onClick={() => del(r.code)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button>}
              </div>
            </div>
            <h3 className="font-bold text-lg text-gray-800">{r.name}</h3>
            <p className="text-xs text-gray-400 mb-3">{r.code} | Niveau {r.level}</p>
            <div className="space-y-1 text-sm text-gray-500">
              <div className="flex justify-between"><span>Utilisateurs</span><span className="font-medium">{r.users_count||0}</span></div>
              <div className="flex justify-between"><span>Permissions</span><span className="font-medium">{r.permissions_count||0}</span></div>
            </div>
          </div>
        ))}
      </div>

      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier le rôle" : "Nouveau rôle"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom *" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.code} onChange={e => setForm({...form, code: e.target.value.toUpperCase()})} placeholder="Code * (ex: MANAGER)" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Description" className="w-full p-2.5 border rounded-xl text-sm" />
          <input type="number" value={form.level} onChange={e => setForm({...form, level: +e.target.value})} placeholder="Niveau hiérarchique" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-violet-500 text-white rounded-xl text-sm font-medium">{edit ? "Modifier" : "Créer"}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}