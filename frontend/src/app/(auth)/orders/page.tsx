"use client"
import { useState, useEffect } from "react"
import { Search, Plus, Download } from "lucide-react"
import { Modal } from "@/components/ui/modal"

const API = "http://localhost:8000/api/v1"
const statusColors = { DRAFT: "bg-gray-100 text-gray-700", PENDING: "bg-amber-100 text-amber-700", APPROVED: "bg-blue-100 text-blue-700", ORDERED: "bg-violet-100 text-violet-700", RECEIVED: "bg-emerald-100 text-emerald-700" }

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ supplier_id: "", notes: "" })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetchOrders = () => {
    fetch(API + "/purchase-orders/", { headers }).then(r => r.json()).then(d => { setOrders(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchOrders() }, [])

  const handleCreate = async () => {
    await fetch(API + "/purchase-orders/create/", { method: "POST", headers, body: JSON.stringify(form) })
    setShowModal(false)
    fetchOrders()
  }

  const handleExport = () => {
    const csv = "Référence,Fournisseur,Date,Montant,Statut\n" + orders.map(o => [o.reference, o.supplier_name, o.order_date, o.total_amount, o.status].join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "commandes.csv"; a.click()
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Commandes</h1><p className="text-sm text-gray-500">{orders.length} commande(s)</p></div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
          <button onClick={() => setShowModal(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Référence</th><th className="text-left px-6 py-3">Fournisseur</th><th className="text-left px-6 py-3">Date</th><th className="text-right px-6 py-3">Montant</th><th className="text-center px-6 py-3">Statut</th></tr></thead>
          <tbody>{orders.map(o => (<tr key={o.id} className="border-b border-gray-50"><td className="px-6 py-4 font-medium">{o.reference}</td><td className="px-6 py-4">{o.supplier_name}</td><td className="px-6 py-4 text-gray-500">{o.order_date}</td><td className="px-6 py-4 text-right font-semibold">{o.total_amount?.toLocaleString()} XAF</td><td className="px-6 py-4 text-center"><span className={"px-2.5 py-1 rounded-full text-xs font-medium " + (statusColors[o.status] || "")}>{o.status}</span></td></tr>))}</tbody></table>
      </div>
      <Modal open={showModal} onClose={() => setShowModal(false)} title="Nouvelle commande">
        <div className="space-y-3">
          <input value={form.supplier_id} onChange={e => setForm({...form, supplier_id: e.target.value})} placeholder="ID du fournisseur (UUID)" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Notes" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={handleCreate} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
