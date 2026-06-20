"use client"
import { useState, useEffect } from "react"
import { Plus, Pencil, Trash2, Download, Search, FolderTree } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function CategoriesPage() {
  const [data, setData] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ name: "", code: "", description: "" })

  const fetchData = () => {
    fetch(API + "/categories/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || d || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const openCreate = () => { setEdit(null); setForm({ name: "", code: "", description: "" }); setShow(true) }
  const openEdit = (c) => { setEdit(c.id); setForm({ name: c.name, code: c.code, description: c.description || "" }); setShow(true) }
  const save = async () => {
    await fetch(edit ? API + "/categories/" + edit + "/" : API + "/categories/", { method: edit ? "PATCH" : "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/categories/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const exp = () => {
    const csv = "Nom,Code,Produits,Enfants,Niveau\n" + data.map(c => [c.name,c.code,c.products_count||0,c.children_count||0,c.level||0].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "categories.csv"; a.click()
  }

  if (loading) return <Loading />
  const f = data.filter(c => (c.name||"").toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Catégories</h1><p className="text-sm text-gray-500">{data.length} catégorie(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border p-6">
        <div className="relative max-w-sm mb-4"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {f.map(c => (
            <div key={c.id} className="p-4 border rounded-2xl hover:shadow-md transition-all">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2"><div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600"><FolderTree size={16} className="text-white" /></div><h3 className="font-semibold">{c.name}</h3></div>
                <div className="flex gap-1">
                  <button onClick={() => openEdit(c)} className="p-1 hover:bg-gray-100 rounded"><Pencil size={12} /></button>
                  <button onClick={() => del(c.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={12} className="text-red-400" /></button>
                </div>
              </div>
              <p className="text-xs text-gray-400">{c.code} | Niv.{c.level} | {c.products_count||0} produits</p>
            </div>
          ))}
        </div>
      </div>
      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier" : "Nouvelle catégorie"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.code} onChange={e => setForm({...form, code: e.target.value})} placeholder="Code" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Description" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">Enregistrer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}