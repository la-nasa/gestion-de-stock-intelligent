"use client"
import { useState, useEffect } from "react"
import { Plus } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { Loading } from "@/components/features/loading"
import { ExportButton } from "@/components/features/export-button"

const API = "http://localhost:8000/api/v1"

export default function TransfersPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ source_warehouse_id: "", destination_warehouse_id: "", notes: "", items: [{ product_id: "", quantity: 1, unit_price: 0 }] })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  useEffect(() => {
    globalThis.fetch(API + "/transfers/", { headers }).then(r => r.json()).then(d => { setData(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const save = async () => {
    await globalThis.fetch(API + "/transfers/create/", { method: "POST", headers, body: JSON.stringify(form) })
    setShow(false); globalThis.location.reload()
  }

  const addItem = () => setForm({...form, items: [...form.items, { product_id: "", quantity: 1, unit_price: 0 }]})
  const updateItem = (i, field, value) => { const items = [...form.items]; items[i][field] = value; setForm({...form, items}) }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Transferts</h1><p className="text-sm text-gray-500">{data.length} transfert(s)</p></div>
        <div className="flex gap-2">
          <ExportButton data={data} filename="transferts.csv" headers={["reference","source_name","destination_name","status"]} />
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg"><Plus size={16} /> Nouveau transfert</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Référence</th><th className="text-left px-6 py-3">Source</th><th className="text-left px-6 py-3">Destination</th><th className="text-center px-6 py-3">Articles</th><th className="text-center px-6 py-3">Statut</th></tr></thead>
          <tbody>{data.map(t => (<tr key={t.id} className="border-b border-gray-50"><td className="px-6 py-4 font-medium">{t.reference}</td><td className="px-6 py-4">{t.source_name}</td><td className="px-6 py-4">{t.destination_name}</td><td className="px-6 py-4 text-center">{t.total_items}</td><td className="px-6 py-4 text-center"><span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">{t.status}</span></td></tr>))}</tbody></table>
      </div>
      <Modal open={show} onClose={() => setShow(false)} title="Nouveau transfert">
        <div className="space-y-3">
          <input value={form.source_warehouse_id} onChange={e => setForm({...form, source_warehouse_id: e.target.value})} placeholder="ID Entrepôt Source" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.destination_warehouse_id} onChange={e => setForm({...form, destination_warehouse_id: e.target.value})} placeholder="ID Entrepôt Destination" className="w-full p-2.5 border rounded-xl text-sm" />
          {form.items.map((item, i) => (
            <div key={i} className="grid grid-cols-3 gap-2">
              <input value={item.product_id} onChange={e => updateItem(i, "product_id", e.target.value)} placeholder="ID Produit" className="p-2 border rounded-lg text-xs" />
              <input type="number" value={item.quantity} onChange={e => updateItem(i, "quantity", Number(e.target.value))} placeholder="Qté" className="p-2 border rounded-lg text-xs" />
              <input type="number" value={item.unit_price} onChange={e => updateItem(i, "unit_price", Number(e.target.value))} placeholder="Prix" className="p-2 border rounded-lg text-xs" />
            </div>
          ))}
          <button onClick={addItem} className="text-xs text-blue-600 hover:underline">+ Ajouter un article</button>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
