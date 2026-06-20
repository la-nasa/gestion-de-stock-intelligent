"use client"
import { useState, useEffect } from "react"
import { Search, Plus, Package, Pencil, Trash2, Download } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form, setForm] = useState({ name: "", reference: "", sku: "", category_id: "", unit_price: 0, min_stock: 0, max_stock: 100, unit: "PIECE", brand: "", description: "", supplier_id: "" })

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
  const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token }

  const fetchP = async () => {
    setLoading(true)
    try {
      const res = await fetch(API + "/products/", { headers })
      const json = await res.json()
      // L'API retourne { success: true, data: { results: [...], count: 33 } }
      const items = json?.data?.results || json?.results || json?.data || []
      setProducts(Array.isArray(items) ? items : [])
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { fetchP() }, [])

  const openCreate = () => { setEdit(null); setForm({ name: "", reference: "", sku: "", category_id: "", unit_price: 0, min_stock: 0, max_stock: 100, unit: "PIECE", brand: "", description: "", supplier_id: "" }); setShow(true) }
  const openEdit = (p) => { setEdit(p.id); setForm({ name: p.name||"", reference: p.reference||"", sku: p.sku||"", category_id: p.category||"", unit_price: p.unit_price||0, min_stock: p.min_stock||0, max_stock: p.max_stock||100, unit: p.unit||"PIECE", brand: p.brand||"", description: p.description||"", supplier_id: p.supplier||"" }); setShow(true) }

  const save = async () => {
    const url = edit ? API + "/products/" + edit + "/" : API + "/products/create/"
    const method = edit ? "PATCH" : "POST"
    await fetch(url, { method, headers, body: JSON.stringify(form) })
    setShow(false); fetchP()
  }

  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/products/" + id + "/", { method: "DELETE", headers }); fetchP() } }

  const exportCSV = () => {
    const csv = "Nom,Réf,SKU,Catégorie,Prix,Stock\n" + products.map(p => [p.name,p.reference,p.sku,p.category_name||"",p.unit_price,p.total_stock].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "produits.csv"; a.click()
  }

  if (loading) return <Loading />

  const filtered = products.filter(p => (p.name||"").toLowerCase().includes(search.toLowerCase()) || (p.reference||"").toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Produits</h1><p className="text-sm text-gray-500">{products.length} produit(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exportCSV} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Exporter</button>
          <button onClick={openCreate} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouveau</button>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-2.5 text-gray-400" /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2 border rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Produit</th><th className="text-left px-6 py-3">Catégorie</th><th className="text-center px-6 py-3">Stock</th><th className="text-right px-6 py-3">Prix</th><th className="text-center px-6 py-3">Actions</th></tr></thead>
          <tbody>
            {filtered.length > 0 ? filtered.map(p => (
              <tr key={p.id} className="border-b hover:bg-gray-50/30">
                <td className="px-6 py-4"><div className="flex items-center gap-3"><Package size={16} className="text-emerald-600" /><div><p className="font-medium">{p.name}</p><p className="text-xs text-gray-400">{p.reference} | SKU: {p.sku}</p></div></div></td>
                <td className="px-6 py-4"><span className="px-2 py-1 rounded-full text-xs bg-blue-50 text-blue-700">{p.category_name || "-"}</span></td>
                <td className="px-6 py-4 text-center"><span className="font-semibold">{p.total_stock || 0}</span></td>
                <td className="px-6 py-4 text-right font-medium">{p.unit_price?.toLocaleString()} {p.currency||"XAF"}</td>
                <td className="px-6 py-4"><div className="flex justify-center gap-1"><button onClick={() => openEdit(p)} className="p-1.5 hover:bg-gray-100 rounded"><Pencil size={14} /></button><button onClick={() => del(p.id)} className="p-1.5 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></div></td>
              </tr>
            )) : <tr><td colSpan={5} className="px-6 py-12 text-center text-gray-400">Aucun produit trouvé</td></tr>}
          </tbody>
        </table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title={edit ? "Modifier" : "Nouveau produit"}>
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom *" className="w-full p-2.5 border rounded-xl text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <input value={form.reference} onChange={e => setForm({...form, reference: e.target.value})} placeholder="Référence *" className="p-2.5 border rounded-xl text-sm" />
            <input value={form.sku} onChange={e => setForm({...form, sku: e.target.value})} placeholder="SKU *" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="text-xs text-gray-500 mb-1 block">Catégorie</label><SelectSearch apiUrl={API + "/categories/"} value={form.category_id} onChange={v => setForm({...form, category_id: v})} placeholder="Sélectionner..." /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Fournisseur</label><SelectSearch apiUrl={API + "/suppliers/"} value={form.supplier_id} onChange={v => setForm({...form, supplier_id: v})} placeholder="Sélectionner..." /></div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <input type="number" value={form.unit_price} onChange={e => setForm({...form, unit_price: +e.target.value})} placeholder="Prix" className="p-2.5 border rounded-xl text-sm" />
            <input type="number" value={form.min_stock} onChange={e => setForm({...form, min_stock: +e.target.value})} placeholder="Stock min" className="p-2.5 border rounded-xl text-sm" />
            <input type="number" value={form.max_stock} onChange={e => setForm({...form, max_stock: +e.target.value})} placeholder="Stock max" className="p-2.5 border rounded-xl text-sm" />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShow(false)} className="px-4 py-2 border rounded-xl text-sm">Annuler</button>
            <button onClick={save} className="px-4 py-2 bg-emerald-500 text-white rounded-xl text-sm font-medium">{edit ? "Modifier" : "Créer"}</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}