"use client"
import { useState, useEffect } from "react"
import { Plus } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SearchBar } from "@/components/features/search-bar"
import { Loading } from "@/components/features/loading"
import { ExportButton } from "@/components/features/export-button"

const API = "http://localhost:8000/api/v1"

export default function StockEntriesPage() {
  const [data, setData] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ warehouse_id: "", notes: "", items: [{ product_id: "", quantity: 1, unit_price: 0 }] })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetch = () => {
    globalThis.fetch(API + "/stock-entries/", { headers }).then(r => r.json()).then(d => { setData(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }
  useEffect(() => { fetch() }, [])

  const save = async () => {
    await globalThis.fetch(API + "/stock-entries/create/", { method: "POST", headers, body: JSON.stringify(form) })
    setShow(false); fetch()
  }

  const addItem = () => setForm({...form, items: [...form.items, { product_id: "", quantity: 1, unit_price: 0 }]})
  const updateItem = (i, field, value) => {
    const items = [...form.items]; items[i][field] = value; setForm({...form, items})
  }

  if (loading) return <Loading />
  const filtered = data.filter(e => (e.reference || "").toLowerCase().includes(search.toLowerCase()) || (e.supplier_name || "").toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Entrées de stock</h1><p className="text-sm text-gray-500">{data.length} entrée(s)</p></div>
        <div className="flex gap-2">
          <ExportButton data={data} filename="entrees.csv" headers={["reference","supplier_name","entry_date","total_amount","status"]} />
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle entrée</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b"><SearchBar value={search} onChange={setSearch} /></div>
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Référence</th><th className="text-left px-6 py-3">Fournisseur</th><th className="text-left px-6 py-3">Date</th><th className="text-right px-6 py-3">Montant</th><th className="text-center px-6 py-3">Statut</th></tr></thead>
          <tbody>{filtered.map(e => (<tr key={e.id} className="border-b border-gray-50"><td className="px-6 py-4 font-medium">{e.reference}</td><td className="px-6 py-4">{e.supplier_name}</td><td className="px-6 py-4 text-gray-500">{e.entry_date}</td><td className="px-6 py-4 text-right font-semibold">{e.total_amount?.toLocaleString()} XAF</td><td className="px-6 py-4 text-center"><span className="px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-700">{e.status}</span></td></tr>))}</tbody></table>
      </div>
      <Modal open={show} onClose={() => setShow(false)} title="Nouvelle entrée de stock">
        <div className="space-y-3">
          <input value={form.warehouse_id} onChange={e => setForm({...form, warehouse_id: e.target.value})} placeholder="ID Entrepôt" className="w-full p-2.5 border rounded-xl text-sm" />
          <input value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Notes" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">Articles :</p>
            {form.items.map((item, i) => (
              <div key={i} className="grid grid-cols-3 gap-2">
                <input value={item.product_id} onChange={e => updateItem(i, "product_id", e.target.value)} placeholder="ID Produit" className="p-2 border rounded-lg text-xs" />
                <input type="number" value={item.quantity} onChange={e => updateItem(i, "quantity", Number(e.target.value))} placeholder="Qté" className="p-2 border rounded-lg text-xs" />
                <input type="number" value={item.unit_price} onChange={e => updateItem(i, "unit_price", Number(e.target.value))} placeholder="Prix" className="p-2 border rounded-lg text-xs" />
              </div>
            ))}
            <button onClick={addItem} className="text-xs text-emerald-600 hover:underline">+ Ajouter un article</button>
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
