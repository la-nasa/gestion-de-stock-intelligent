"use client"
import { useState, useEffect } from "react"
import { Plus, Download, Trash2, Wrench } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function MaintenancePage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ product_id: "", type: "PREVENTIVE", description: "", scheduled_date: new Date().toISOString().split("T")[0], technician: "" })

  const fetchData = () => {
    // Utiliser les produits comme équipements
    fetch(API + "/products/", { headers: H() }).then(r => r.json()).then(d => {
      const products = d?.data?.results || d.data || []
      setData(products.slice(0, 15).map((p,i) => ({
        id: p.id, equipment: p.name, type: ["Préventive","Corrective","Prédictive"][i%3],
        date: new Date(2026, 6, i+1).toISOString().split("T")[0], status: ["Planifiée","En cours","Terminée"][i%3],
        technician: ["Tech A","Tech B","Tech C"][i%3]
      })))
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const create = () => {
    setData([...data, { id: Date.now(), equipment: "Nouvel équipement", type: form.type, date: form.scheduled_date, status: "Planifiée", technician: form.technician || "Tech A" }])
    setShow(false)
  }
  const del = (id) => { setData(data.filter(d => d.id !== id)) }

  const exp = () => {
    const csv = "Équipement,Type,Date,Technicien,Statut\n" + data.map(m => [m.equipment,m.type,m.date,m.technician,m.status].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "maintenance.csv"; a.click()
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Maintenance</h1><p className="text-sm text-gray-500">{data.length} enregistrements</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-violet-500 to-purple-600 hover:shadow-lg"><Plus size={16} /> Nouvelle</button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 shadow-sm border text-center"><p className="text-3xl font-bold text-blue-600">{data.filter(d=>d.status==="Planifiée").length}</p><p className="text-sm text-gray-500">Planifiées</p></div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border text-center"><p className="text-3xl font-bold text-amber-600">{data.filter(d=>d.status==="En cours").length}</p><p className="text-sm text-gray-500">En cours</p></div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border text-center"><p className="text-3xl font-bold text-emerald-600">{data.filter(d=>d.status==="Terminée").length}</p><p className="text-sm text-gray-500">Terminées</p></div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Équipement</th><th className="text-left px-6 py-3">Type</th><th className="text-left px-6 py-3">Date</th><th className="text-left px-6 py-3">Technicien</th><th className="text-center px-6 py-3">Statut</th><th className="text-center px-6 py-3"></th></tr></thead>
        <tbody>{data.map(m => (<tr key={m.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 font-medium">{m.equipment}</td><td className="px-6 py-4">{m.type}</td><td className="px-6 py-4 text-gray-500">{m.date}</td><td className="px-6 py-4">{m.technician}</td><td className="px-6 py-4 text-center"><span className={"px-2 py-1 rounded-full text-xs "+(m.status==="Planifiée"?"bg-blue-100 text-blue-700":m.status==="En cours"?"bg-amber-100 text-amber-700":"bg-emerald-100 text-emerald-700")}>{m.status}</span></td><td className="px-6 py-4"><button onClick={() => del(m.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title="Nouvelle maintenance">
        <div className="space-y-3">
          <SelectSearch apiUrl={API + "/products/"} value={form.product_id} onChange={v => setForm({...form, product_id: v})} placeholder="Équipement *" />
          <select value={form.type} onChange={e => setForm({...form, type: e.target.value})} className="w-full p-2.5 border rounded-xl text-sm">
            <option value="PREVENTIVE">Préventive</option><option value="CORRECTIVE">Corrective</option><option value="PREDICTIVE">Prédictive</option>
          </select>
          <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Description" className="w-full p-2.5 border rounded-xl text-sm" />
          <input type="date" value={form.scheduled_date} onChange={e => setForm({...form, scheduled_date: e.target.value})} className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.technician} onChange={e => setForm({...form, technician: e.target.value})} placeholder="Technicien" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={create} className="px-4 py-2 bg-violet-500 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}