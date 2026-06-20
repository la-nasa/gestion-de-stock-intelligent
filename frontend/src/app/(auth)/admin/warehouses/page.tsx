"use client"
import { useState, useEffect } from "react"
import { Plus, Pencil, Trash2, Download, Search, Warehouse } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const T = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + T(), ...m })

export default function WarehousesPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ name: "", code: "", campus_id: "", type: "SECONDARY", capacity: 0, address: "" })

  const fetchData = () => {
    fetch(API + "/warehouses/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const openCreate = () => { setEdit(null); setForm({ name: "", code: "", campus_id: "", type: "SECONDARY", capacity: 0, address: "" }); setShow(true) }
  const openEdit = (w) => { setEdit(w.id); setForm({ name: w.name, code: w.code, campus_id: w.campus_id||"", type: w.type||"SECONDARY", capacity: w.capacity||0, address: w.address||"" }); setShow(true) }
  const save = async () => {
    const url = edit ? API + "/warehouses/" + edit + "/" : API + "/warehouses/create/"
    await fetch(url, { method: edit ? "PATCH" : "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/warehouses/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const exp = () => {
    const csv = "Nom,Code,Campus,Type,Capacité\n" + data.map(w => [w.name,w.code,w.campus_name,w.type,w.capacity].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "entrepots.csv"; a.click()
  }

  if (loading) return <Loading />
  const f = data.filter(w => (w.name||"").toLowerCase().includes(""))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Entrepôts</h1><p className="text-sm text-gray-500">{data.length} entrepôt(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-amber-500 to-orange-600 hover:shadow-lg"><Plus size={16} /> Nouvel entrepôt</button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {f.map(w => (
          <div key={w.id} className="bg-white rounded-2xl p-5 shadow-sm border hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600"><Warehouse size={18} className="text-white" /></div>
              <div className="flex gap-1">
                <button onClick={() => openEdit(w)} className="p-1 hover:bg-gray-100 rounded"><Pencil size={14} /></button>
                <button onClick={() => del(w.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button>
              </div>
            </div>
            <h3 className="font-semibold text-gray-800">{w.name}</h3>
            <p className="text-xs text-gray-400">{w.code} | {w.type} | {w.campus_name}</p>
            <p className="text-sm text-gray-500 mt-2">Capacité: {w.capacity} m²</p>
          </div>
        ))}
      </div>
      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier" : "Nouvel entrepôt"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom *" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.code} onChange={e => setForm({...form, code: e.target.value})} placeholder="Code *" className="w-full p-2.5 border rounded-xl text-sm" />
          <SelectSearch apiUrl={API + "/campuses/"} value={form.campus_id} onChange={v => setForm({...form, campus_id: v})} placeholder="Campus" />
          <div className="grid grid-cols-2 gap-3">
            <select value={form.type} onChange={e => setForm({...form, type: e.target.value})} className="p-2.5 border rounded-xl text-sm">
              <option value="MAIN">Principal</option><option value="SECONDARY">Secondaire</option>
            </select>
            <input type="number" value={form.capacity} onChange={e => setForm({...form, capacity: +e.target.value})} placeholder="Capacité (m²)" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-amber-500 text-white rounded-xl text-sm font-medium">{edit ? "Modifier" : "Créer"}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}