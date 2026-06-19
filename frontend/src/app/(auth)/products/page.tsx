"use client"
import { useState } from "react"
import { Search, Plus, Download, Filter, Package, Pencil, Trash2, QrCode, Star } from "lucide-react"

const products = [
  { name: "Ordinateur Dell Latitude 5540", ref: "DELL-LAT-5540", cat: "Informatique", stock: 45, min: 10, price: "450 000 XAF", supplier: "TechSupply", status: "normal" },
  { name: "Imprimante HP LaserJet Pro", ref: "HP-LJ-MFP4101", cat: "Périphériques", stock: 8, min: 5, price: "180 000 XAF", supplier: "BureauPlus", status: "low" },
  { name: "Papier A4 80g (ramette)", ref: "PAP-A4-80", cat: "Papeterie", stock: 520, min: 100, price: "2 500 XAF", supplier: "Papeterie Moderne", status: "normal" },
  { name: "Projecteur Epson EB-X51", ref: "EPS-EBX51", cat: "Périphériques", stock: 2, min: 3, price: "300 000 XAF", supplier: "TechSupply", status: "out" },
  { name: "Microscope Olympus CX23", ref: "OLY-CX23", cat: "Laboratoire", stock: 6, min: 2, price: "500 000 XAF", supplier: "LaboEquip", status: "normal" },
  { name: "Bureau Enseignant", ref: "BUR-ENS-001", cat: "Mobilier", stock: 12, min: 5, price: "120 000 XAF", supplier: "Africa Mobilier", status: "normal" },
  { name: "Climatiseur Split 18000 BTU", ref: "CLIM-SPLIT-18K", cat: "Climatisation", stock: 4, min: 3, price: "250 000 XAF", supplier: "ClimTech", status: "low" },
]

const statusBadge = { normal: "bg-emerald-100 text-emerald-700", low: "bg-amber-100 text-amber-700", out: "bg-red-100 text-red-700" }
const statusLabel = { normal: "Normal", low: "Stock bas", out: "Rupture" }

export default function ProductsPage() {
  const [search, setSearch] = useState("")
  const filtered = products.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.ref.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Produits</h1>
          <p className="text-sm text-gray-500 mt-1">{products.length} produit(s) au total</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
            <Download size={16} /> Exporter
          </button>
          <button className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg transition-all">
            <Plus size={16} /> Nouveau produit
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20" />
          </div>
          <button className="flex items-center gap-2 px-4 py-2.5 text-sm border border-gray-200 rounded-xl hover:bg-gray-50"><Filter size={16} /> Filtres</button>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50/50">
            <tr>
              <th className="text-left px-6 py-3.5 font-semibold text-gray-600">Produit</th>
              <th className="text-left px-6 py-3.5 font-semibold text-gray-600">Catégorie</th>
              <th className="text-center px-6 py-3.5 font-semibold text-gray-600">Stock</th>
              <th className="text-right px-6 py-3.5 font-semibold text-gray-600">Prix</th>
              <th className="text-left px-6 py-3.5 font-semibold text-gray-600">Fournisseur</th>
              <th className="text-center px-6 py-3.5 font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/30 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center"><Package size={16} className="text-emerald-600" /></div>
                    <div><p className="font-medium text-gray-800">{p.name}</p><p className="text-xs text-gray-400">{p.ref}</p></div>
                  </div>
                </td>
                <td className="px-6 py-4"><span className="px-2.5 py-1 rounded-full text-xs bg-blue-50 text-blue-700">{p.cat}</span></td>
                <td className="px-6 py-4 text-center">
                  <span className={`font-semibold ${p.status === "out" ? "text-red-600" : p.status === "low" ? "text-amber-600" : "text-emerald-600"}`}>{p.stock}</span>
                  {p.status !== "normal" && <span className={`ml-2 text-xs px-1.5 py-0.5 rounded-full ${statusBadge[p.status]}`}>{statusLabel[p.status]}</span>}
                </td>
                <td className="px-6 py-4 text-right font-medium text-gray-700">{p.price}</td>
                <td className="px-6 py-4 text-gray-500">{p.supplier}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center justify-center gap-1">
                    <button className="p-1.5 hover:bg-gray-100 rounded-lg"><Pencil size={14} className="text-gray-400" /></button>
                    <button className="p-1.5 hover:bg-emerald-50 rounded-lg"><QrCode size={14} className="text-emerald-500" /></button>
                    <button className="p-1.5 hover:bg-red-50 rounded-lg"><Trash2 size={14} className="text-red-400" /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}