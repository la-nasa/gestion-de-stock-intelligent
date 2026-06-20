"use client"
import { useState, useEffect } from "react"
import { Search, Plus, Building2, Phone, Mail, Download, Pencil, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"

const API = "http://localhost:8000/api/v1"

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: "", code: "", email: "", phone: "", contact_person: "", city: "", category: "" })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetchSuppliers = () => {
    fetch(API + "/suppliers/", { headers }).then(r => r.json()).then(d => { setSuppliers(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchSuppliers() }, [])

  const handleCreate = () => {
    setForm({ name: "", code: "", email: "", phone: "", contact_person: "", city: "", category: "" })
    setShowModal(true)
  }

  const handleSave = async () => {
    await fetch(API + "/suppliers/create/", { method: "POST", headers, body: JSON.stringify(form) })
    setShowModal(false)
    fetchSuppliers()
  }

  const handleExport = () => {
    const csv = "Nom,Code,Email,Téléphone,Contact,Ville\n" + suppliers.map(s => [s.name, s.code, s.email, s.phone, s.contact_person, s.city].join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "fournisseurs.csv"; a.click()
  }

  const filtered = suppliers.filter(s => (s.name || "").toLowerCase().includes(search.toLowerCase()))

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Fournisseurs</h1><p className="text-sm text-gray-500">{suppliers.length} fournisseur(s)</p></div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
          <button onClick={handleCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg"><Plus size={16} /> Nouveau</button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(s => (
          <div key={s.id} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-3"><div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600"><Building2 size={18} className="text-white" /></div><div><h3 className="font-semibold">{s.name}</h3><p className="text-xs text-gray-400">{s.code}</p></div></div>
            <div className="space-y-1 text-sm text-gray-500"><div className="flex items-center gap-2"><Phone size={12} /> {s.phone}</div><div className="flex items-center gap-2"><Mail size={12} /> {s.email}</div></div>
          </div>
        ))}
      </div>
      <Modal open={showModal} onClose={() => setShowModal(false)} title="Nouveau fournisseur">
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom" className="w-full p-2.5 border rounded-xl text-sm" />
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
            <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
