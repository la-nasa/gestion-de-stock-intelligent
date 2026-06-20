"use client"
import { useState, useEffect } from "react"
import { Plus, Download, Trash2, Eye } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })
const SC = { DRAFT: "bg-gray-100 text-gray-700", PENDING: "bg-amber-100 text-amber-700", APPROVED: "bg-blue-100 text-blue-700", ORDERED: "bg-violet-100 text-violet-700", RECEIVED: "bg-emerald-100 text-emerald-700" }

export default function OrdersPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [detail, setDetail] = useState(null)
  const [form, setForm] = useState({ supplier_id: "", product_id: "", quantity: 1, unit_price: 0, notes: "" })

  const fetchData = () => {
    fetch(API + "/purchase-orders/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const save = async () => {
    if (!form.supplier_id || !form.product_id) return alert("Champs obligatoires")
    await fetch(API + "/purchase-orders/create/", { method: "POST", headers: H(), body: JSON.stringify(form) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/purchase-orders/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }
  const viewDetail = async (id) => {
    const r = await fetch(API + "/purchase-orders/" + id + "/", { headers: H() })
    const d = await r.json()
    setDetail(d.data || d)
  }

  const exp = () => {
    const csv = "Réf,Fournisseur,Date,Montant,Statut\n" + data.map(o => [o.reference,o.supplier_name,o.order_date,o.total_amount,o.status].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "commandes.csv"; a.click()
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Commandes</h1><p className="text-sm text-gray-500">{data.length} commande(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Réf</th><th className="text-left px-6 py-3">Fournisseur</th><th className="text-left px-6 py-3">Date</th><th className="text-right px-6 py-3">Montant</th><th className="text-center px-6 py-3">Statut</th><th className="text-center px-6 py-3"></th></tr></thead>
        <tbody>{data.map(o => (<tr key={o.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 font-medium">{o.reference}</td><td className="px-6 py-4">{o.supplier_name}</td><td className="px-6 py-4 text-gray-500">{o.order_date}</td><td className="px-6 py-4 text-right font-semibold">{o.total_amount?.toLocaleString()} XAF</td><td className="px-6 py-4 text-center"><span className={"px-2 py-1 rounded-full text-xs font-medium "+(SC[o.status]||"")}>{o.status}</span></td><td className="px-6 py-4"><div className="flex justify-center gap-1"><button onClick={() => viewDetail(o.id)} className="p-1 hover:bg-gray-100 rounded"><Eye size={14} /></button><button onClick={() => del(o.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></div></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title="Nouvelle commande">
        <div className="space-y-3">
          <SelectSearch apiUrl={API + "/suppliers/"} value={form.supplier_id} onChange={v => setForm({...form, supplier_id: v})} placeholder="Fournisseur *" />
          <SelectSearch apiUrl={API + "/products/"} value={form.product_id} onChange={v => setForm({...form, product_id: v})} placeholder="Produit *" />
          <div className="grid grid-cols-2 gap-3">
            <input type="number" value={form.quantity} onChange={e => setForm({...form, quantity: +e.target.value})} placeholder="Quantité" className="p-2.5 border rounded-xl text-sm" />
            <input type="number" value={form.unit_price} onChange={e => setForm({...form, unit_price: +e.target.value})} placeholder="Prix unitaire" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer</button>
          </div>
        </div>
      </Modal>

      {detail && (
        <Modal open={!!detail} onClose={() => setDetail(null)} title={"Détail " + detail.reference}>
          <div className="space-y-2 text-sm">
            <p><strong>Fournisseur:</strong> {detail.supplier_name}</p>
            <p><strong>Date:</strong> {detail.order_date}</p>
            <p><strong>Montant:</strong> {detail.total_amount?.toLocaleString()} XAF</p>
            <p><strong>Statut:</strong> {detail.status}</p>
            {detail.lines?.length > 0 && (
              <div className="mt-3">
                <p className="font-medium mb-1">Lignes:</p>
                {detail.lines.map((l,i) => (
                  <div key={i} className="flex justify-between text-xs py-1 border-b">
                    <span>{l.product_name}</span>
                    <span>{l.quantity} x {l.unit_price?.toLocaleString()} = {l.total_price?.toLocaleString()} XAF</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}