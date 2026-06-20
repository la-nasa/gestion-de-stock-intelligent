"use client"
import { useState, useEffect } from "react"
import { Plus, Download, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function OutputsPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ warehouse_id: "", product_id: "", quantity: 1, reason: "INTERNAL_USE", notes: "" })

  const fetchData = () => {
    fetch(API + "/stock-outputs/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const save = async () => {
    if (!form.warehouse_id || !form.product_id) return alert("Champs obligatoires")
    await fetch(API + "/stock-outputs/create/", { method: "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/stock-outputs/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const exp = () => {
    const csv = "Réf,Motif,Date,Montant,Statut\n" + data.map(o => [o.reference,o.reason,o.output_date||"",o.total_amount||0,o.status].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "sorties.csv"; a.click()
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Sorties de stock</h1><p className="text-sm text-gray-500">{data.length} sortie(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-rose-500 to-red-500 hover:shadow-lg"><Plus size={16} /> Nouvelle sortie</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Réf</th><th className="text-left px-6 py-3">Motif</th><th className="text-right px-6 py-3">Montant</th><th className="text-center px-6 py-3">Statut</th><th className="text-center px-6 py-3"></th></tr></thead>
        <tbody>{data.map(o => (<tr key={o.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 font-medium">{o.reference}</td><td className="px-6 py-4">{o.reason}</td><td className="px-6 py-4 text-right font-semibold">{o.total_amount?.toLocaleString()} XAF</td><td className="px-6 py-4 text-center">{o.status}</td><td className="px-6 py-4"><button onClick={() => del(o.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title="Nouvelle sortie">
        <div className="space-y-3">
          <SelectSearch apiUrl={API + "/stocks/"} value={form.warehouse_id} onChange={v => setForm({...form, warehouse_id: v})} labelField="warehouse_name" valueField="warehouse" placeholder="Entrepôt *" />
          <SelectSearch apiUrl={API + "/products/"} value={form.product_id} onChange={v => setForm({...form, product_id: v})} placeholder="Produit *" />
          <input type="number" value={form.quantity} onChange={e => setForm({...form, quantity: +e.target.value})} placeholder="Quantité *" className="w-full p-2.5 border rounded-xl text-sm" />
          <select value={form.reason} onChange={e => setForm({...form, reason: e.target.value})} className="w-full p-2.5 border rounded-xl text-sm">
            <option value="INTERNAL_USE">Usage interne</option><option value="DAMAGE">Dommage</option><option value="LOSS">Perte</option><option value="EXPIRED">Expiré</option>
          </select>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-rose-500 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}