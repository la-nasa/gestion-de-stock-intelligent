"use client"
import { useState, useEffect } from "react"
import { Plus, Download, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function TransfersPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ source_warehouse_id: "", destination_warehouse_id: "", product_id: "", quantity: 1, notes: "" })

  const fetchData = () => {
    fetch(API + "/transfers/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const save = async () => {
    if (!form.source_warehouse_id || !form.destination_warehouse_id || !form.product_id) return alert("Champs obligatoires")
    await fetch(API + "/transfers/create/", { method: "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/transfers/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Transferts</h1><p className="text-sm text-gray-500">{data.length} transfert(s)</p></div>
        <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg"><Plus size={16} /> Nouveau transfert</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Réf</th><th className="text-left px-6 py-3">Source</th><th className="text-left px-6 py-3">Destination</th><th className="text-center px-6 py-3">Articles</th><th className="text-center px-6 py-3">Statut</th></tr></thead>
        <tbody>{data.map(t => (<tr key={t.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 font-medium">{t.reference}</td><td className="px-6 py-4">{t.source_name}</td><td className="px-6 py-4">{t.destination_name}</td><td className="px-6 py-4 text-center">{t.total_items}</td><td className="px-6 py-4 text-center"><span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">{t.status}</span></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title="Nouveau transfert">
        <div className="space-y-3">
          <SelectSearch apiUrl={API + "/stocks/"} value={form.source_warehouse_id} onChange={v => setForm({...form, source_warehouse_id: v})} labelField="warehouse_name" valueField="warehouse" placeholder="Entrepôt source *" />
          <SelectSearch apiUrl={API + "/stocks/"} value={form.destination_warehouse_id} onChange={v => setForm({...form, destination_warehouse_id: v})} labelField="warehouse_name" valueField="warehouse" placeholder="Entrepôt destination *" />
          <SelectSearch apiUrl={API + "/products/"} value={form.product_id} onChange={v => setForm({...form, product_id: v})} placeholder="Produit *" />
          <input type="number" value={form.quantity} onChange={e => setForm({...form, quantity: +e.target.value})} placeholder="Quantité *" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}