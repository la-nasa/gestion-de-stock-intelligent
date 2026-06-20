"use client"
import { useState, useEffect } from "react"
import { Search, Plus, Package, Pencil, Trash2, Download } from "lucide-react"
import { Modal } from "@/components/ui/modal"

const API = "http://localhost:8000/api/v1"

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: "", reference: "", sku: "", category_id: "", unit_price: 0, min_stock: 0, unit: "PIECE", brand: "", description: "" })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetchProducts = () => {
    fetch(API + "/products/", { headers }).then(r => r.json()).then(d => { setProducts(d.data?.results || []); setLoading(false) }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchProducts() }, [])

  const handleDelete = async (id) => {
    if (!confirm("Supprimer ?")) return
    await fetch(API + "/products/" + id + "/", { method: "DELETE", headers })
    fetchProducts()
  }

  const handleEdit = (p) => {
    setEditing(p.id)
    setForm({ name: p.name || "", reference: p.reference || "", sku: p.sku || "", category_id: p.category || "", unit_price: p.unit_price || 0, min_stock: p.min_stock || 0, unit: p.unit || "PIECE", brand: p.brand || "", description: p.description || "" })
    setShowModal(true)
  }

  const handleCreate = () => {
    setEditing(null)
    setForm({ name: "", reference: "", sku: "", category_id: "", unit_price: 0, min_stock: 0, unit: "PIECE", brand: "", description: "" })
    setShowModal(true)
  }

  const handleSave = async () => {
    const url = editing ? API + "/products/" + editing + "/" : API + "/products/create/"
    const method = editing ? "PATCH" : "POST"
    await fetch(url, { method, headers, body: JSON.stringify(form) })
    setShowModal(false)
    fetchProducts()
  }

  const handleExport = () => {
    const csv = "Nom,Référence,SKU,Catégorie,Prix,Stock\n" + products.map(p => [p.name, p.reference, p.sku, p.category_name, p.unit_price, p.total_stock].join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a"); a.href = url; a.download = "produits.csv"; a.click()
  }

  const filtered = products.filter(p => (p.name || "").toLowerCase().includes(search.toLowerCase()))

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div></div>

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Produits</h1><p className="text-sm text-gray-500">{products.length} produit(s)</p></div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
          <button onClick={handleCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouveau</button>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Produit</th><th className="text-left px-6 py-3">Catégorie</th><th className="text-center px-6 py-3">Stock</th><th className="text-right px-6 py-3">Prix</th><th className="text-center px-6 py-3">Actions</th></tr></thead>
          <tbody>
            {filtered.map(p => (
              <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50/30">
                <td className="px-6 py-4"><div className="flex items-center gap-3"><Package size={16} className="text-emerald-600" /><div><p className="font-medium">{p.name}</p><p className="text-xs text-gray-400">{p.reference}</p></div></div></td>
                <td className="px-6 py-4"><span className="px-2 py-1 rounded-full text-xs bg-blue-50 text-blue-700">{p.category_name}</span></td>
                <td className="px-6 py-4 text-center font-semibold">{p.total_stock}</td>
                <td className="px-6 py-4 text-right">{p.unit_price?.toLocaleString()} XAF</td>
                <td className="px-6 py-4"><div className="flex justify-center gap-1"><button onClick={() => handleEdit(p)} className="p-1.5 hover:bg-gray-100 rounded-lg"><Pencil size={14} /></button><button onClick={() => handleDelete(p.id)} className="p-1.5 hover:bg-red-50 rounded-lg"><Trash2 size={14} className="text-red-400" /></button></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={showModal} onClose={() => setShowModal(false)} title={editing ? "Modifier le produit" : "Nouveau produit"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <input value={form.reference} onChange={e => setForm({...form, reference: e.target.value})} placeholder="Référence" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.sku} onChange={e => setForm({...form, sku: e.target.value})} placeholder="SKU" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <input value={form.brand} onChange={e => setForm({...form, brand: e.target.value})} placeholder="Marque" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="grid grid-cols-3 gap-3">
            <input type="number" value={form.unit_price} onChange={e => setForm({...form, unit_price: Number(e.target.value)})} placeholder="Prix" className="p-2.5 border rounded-xl text-sm" />
            <input type="number" value={form.min_stock} onChange={e => setForm({...form, min_stock: Number(e.target.value)})} placeholder="Stock min" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.category_id} onChange={e => setForm({...form, category_id: e.target.value})} placeholder="ID Catégorie" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={handleSave} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">{editing ? "Modifier" : "Créer"}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
