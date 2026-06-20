"use client"
import { useState, useEffect } from "react"
import { Plus, Pencil, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SearchBar } from "@/components/features/search-bar"
import { Loading } from "@/components/features/loading"
import { EmptyState } from "@/components/features/empty-state"
import { ExportButton } from "@/components/features/export-button"

const API = "http://localhost:8000/api/v1"

export default function CategoriesPage() {
  const [data, setData] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ name: "", code: "", description: "", parent_id: "" })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetch = () => {
    globalThis.fetch(API + "/categories/", { headers }).then(r => r.json()).then(d => { setData(d.data || []); setLoading(false) }).catch(() => setLoading(false))
  }
  useEffect(() => { fetch() }, [])

  const openCreate = () => { setEdit(null); setForm({ name: "", code: "", description: "", parent_id: "" }); setShow(true) }
  const openEdit = (c) => { setEdit(c.id); setForm({ name: c.name, code: c.code, description: c.description || "", parent_id: c.parent || "" }); setShow(true) }
  const save = async () => {
    const url = edit ? API + "/categories/" + edit + "/" : API + "/categories/"
    const method = edit ? "PATCH" : "POST"
    await globalThis.fetch(url, { method, headers, body: JSON.stringify(form) })
    setShow(false); fetch()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await globalThis.fetch(API + "/categories/" + id + "/", { method: "DELETE", headers }); fetch() } }

  if (loading) return <Loading />
  const filtered = data.filter(c => (c.name || "").toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Catégories</h1><p className="text-sm text-gray-500">{data.length} catégorie(s)</p></div>
        <div className="flex gap-2">
          <ExportButton data={data} filename="categories.csv" headers={["name","code","level","products_count","children_count"]} />
          <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <SearchBar value={search} onChange={setSearch} placeholder="Rechercher une catégorie..." />
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(c => (
            <div key={c.id} className="p-4 border rounded-2xl hover:shadow-md transition-all">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-800">{c.name}</h3>
                <div className="flex gap-1">
                  <button onClick={() => openEdit(c)} className="p-1 hover:bg-gray-100 rounded"><Pencil size={12} /></button>
                  <button onClick={() => del(c.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={12} className="text-red-400" /></button>
                </div>
              </div>
              <p className="text-xs text-gray-400">{c.code} | Niveau {c.level}</p>
              <div className="flex gap-3 mt-2 text-xs text-gray-500"><span>{c.products_count} produits</span><span>{c.children_count} enfants</span></div>
            </div>
          ))}
          {filtered.length === 0 && <EmptyState message="Aucune catégorie trouvée" />}
        </div>
      </div>
      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier" : "Nouvelle catégorie"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.code} onChange={e => setForm({...form, code: e.target.value})} placeholder="Code" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Description" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.parent_id} onChange={e => setForm({...form, parent_id: e.target.value})} placeholder="ID Parent (optionnel)" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">Enregistrer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
