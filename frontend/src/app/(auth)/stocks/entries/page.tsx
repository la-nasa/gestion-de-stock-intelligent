"use client"
import { useState, useEffect } from "react"
import { Plus, Download, Search, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function EntriesPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ warehouse_id: "", supplier_id: "", product_id: "", quantity: 1, unit_price: 0, notes: "" })

  const fetchData = () => {
    fetch(API + "/stock-entries/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const save = async () => {
    if (!form.warehouse_id || !form.product_id || form.quantity <= 0) return alert("Remplissez tous les champs obligatoires")
    await fetch(API + "/stock-entries/create/", { method: "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/stock-entries/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }

  const exp = () => {
    const csv = "Réf,Fournisseur,Date,Montant,Statut\n" + data.map(e => [e.reference,e.supplier_name||"",e.entry_date||"",e.total_amount||0,e.status].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "entrees.csv"; a.click()
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Entrées de stock</h1><p className="text-sm text-gray-500">{data.length} entrée(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle entrée</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Réf</th><th className="text-left px-6 py-3">Fournisseur</th><th className="text-left px-6 py-3">Date</th><th className="text-right px-6 py-3">Montant</th><th className="text-center px-6 py-3">Statut</th><th className="text-center px-6 py-3"></th></tr></thead>
        <tbody>{data.map(e => (<tr key={e.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 font-medium">{e.reference}</td><td className="px-6 py-4">{e.supplier_name||"-"}</td><td className="px-6 py-4 text-gray-500">{e.entry_date}</td><td className="px-6 py-4 text-right font-semibold">{e.total_amount?.toLocaleString()} XAF</td><td className="px-6 py-4 text-center"><span className="px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-700">{e.status}</span></td><td className="px-6 py-4"><button onClick={() => del(e.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title="Nouvelle entrée">
        <div className="space-y-3">
          <div><label className="text-xs text-gray-500 mb-1 block">Entrepôt *</label><SelectSearch apiUrl={API + "/stocks/"} value={form.warehouse_id} onChange={v => setForm({...form, warehouse_id: v})} labelField="warehouse_name" valueField="warehouse" placeholder="Sélectionner..." /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Fournisseur</label><SelectSearch apiUrl={API + "/suppliers/"} value={form.supplier_id} onChange={v => setForm({...form, supplier_id: v})} placeholder="Sélectionner..." /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Produit *</label><SelectSearch apiUrl={API + "/products/"} value={form.product_id} onChange={v => setForm({...form, product_id: v})} placeholder="Sélectionner..." /></div>
          <div className="grid grid-cols-2 gap-3">
            <input type="number" value={form.quantity} onChange={e => setForm({...form, quantity: +e.target.value})} placeholder="Quantité *" className="p-2.5 border rounded-xl text-sm" />
            <input type="number" value={form.unit_price} onChange={e => setForm({...form, unit_price: +e.target.value})} placeholder="Prix unitaire" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <input value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Notes" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}