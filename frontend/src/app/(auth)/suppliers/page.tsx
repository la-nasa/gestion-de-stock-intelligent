"use client"
import { useState, useEffect } from "react"
import { Plus, Pencil, Trash2, Download, Search, Building2, Phone, Mail, Star } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function SuppliersPage() {
  const [data, setData] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ name: "", code: "", email: "", phone: "", contact_person: "", city: "", category: "" })

  const fetchData = () => {
    fetch(API + "/suppliers/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || d || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const openCreate = () => { setEdit(null); setForm({ name: "", code: "", email: "", phone: "", contact_person: "", city: "", category: "" }); setShow(true) }
  const openEdit = (s) => { setEdit(s.id); setForm({ name: s.name, code: s.code, email: s.email||"", phone: s.phone||"", contact_person: s.contact_person||"", city: s.city||"", category: s.category||"" }); setShow(true) }
  const save = async () => {
    const url = edit ? API + "/suppliers/" + edit + "/" : API + "/suppliers/create/"
    await fetch(url, { method: edit ? "PATCH" : "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/suppliers/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const exp = () => {
    const csv = "Nom,Code,Email,Téléphone,Contact,Ville\n" + data.map(s => [s.name,s.code,s.email,s.phone,s.contact_person,s.city].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "fournisseurs.csv"; a.click()
  }

  if (loading) return <Loading />
  const f = data.filter(s => (s.name||"").toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Fournisseurs</h1><p className="text-sm text-gray-500">{data.length} fournisseur(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg"><Plus size={16} /> Nouveau</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border p-6">
        <div className="relative max-w-sm mb-4"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {f.map(s => (
            <div key={s.id} className="p-5 border rounded-2xl hover:shadow-md transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600"><Building2 size={18} className="text-white" /></div>
                <div className="flex gap-1">
                  {Array.from({length: s.rating||3}).map((_,j) => <Star key={j} size={12} className="text-amber-400 fill-amber-400" />)}
                </div>
              </div>
              <h3 className="font-semibold">{s.name}</h3>
              <p className="text-xs text-gray-400 mb-2">{s.code} | {s.category||"Général"}</p>
              <div className="text-xs text-gray-500 space-y-1"><div className="flex items-center gap-1"><Phone size={10} />{s.phone}</div><div className="flex items-center gap-1"><Mail size={10} />{s.email}</div></div>
              <div className="flex gap-1 mt-3 pt-3 border-t">
                <button onClick={() => openEdit(s)} className="flex-1 py-1.5 text-xs border rounded-lg hover:bg-gray-50"><Pencil size={10} className="inline mr-1" />Modifier</button>
                <button onClick={() => del(s.id)} className="flex-1 py-1.5 text-xs border border-red-200 rounded-lg text-red-500 hover:bg-red-50"><Trash2 size={10} className="inline mr-1" />Supprimer</button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier" : "Nouveau fournisseur"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom *" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <input value={form.code} onChange={e => setForm({...form, code: e.target.value})} placeholder="Code" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="Email" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <input value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} placeholder="Téléphone" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.contact_person} onChange={e => setForm({...form, contact_person: e.target.value})} placeholder="Personne contact" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <input value={form.city} onChange={e => setForm({...form, city: e.target.value})} placeholder="Ville" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="Catégorie" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium">{edit ? "Modifier" : "Créer"}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}