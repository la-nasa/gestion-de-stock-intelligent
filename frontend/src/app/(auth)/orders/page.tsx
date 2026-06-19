"use client"
import { Search, Plus, Eye, Check, X, Package } from "lucide-react"

const orders = [
  { ref: "BC-2026-0001", supplier: "TechSupply Cameroun", date: "15/06/2026", total: "2 450 000 XAF", items: 5, status: "RECEIVED" },
  { ref: "BC-2026-0002", supplier: "BureauPlus SARL", date: "12/06/2026", total: "850 000 XAF", items: 3, status: "ORDERED" },
  { ref: "BC-2026-0003", supplier: "LaboEquip Afrique", date: "10/06/2026", total: "1 200 000 XAF", items: 4, status: "APPROVED" },
  { ref: "BC-2026-0004", supplier: "Papeterie Moderne", date: "08/06/2026", total: "350 000 XAF", items: 2, status: "PENDING" },
]

const statusCfg: Record<string, { label: string; color: string }> = {
  DRAFT: { label: "Brouillon", color: "bg-gray-100 text-gray-700" },
  PENDING: { label: "En attente", color: "bg-amber-100 text-amber-700" },
  APPROVED: { label: "Approuvée", color: "bg-blue-100 text-blue-700" },
  ORDERED: { label: "Commandée", color: "bg-violet-100 text-violet-700" },
  RECEIVED: { label: "Reçue", color: "bg-emerald-100 text-emerald-700" },
}

export default function OrdersPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Commandes</h1><p className="text-sm text-gray-500 mt-1">Gestion des commandes fournisseurs</p></div>
        <button className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle commande</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "En attente", value: 2, color: "from-amber-500 to-orange-500" },
          { label: "Approuvées", value: 1, color: "from-blue-500 to-indigo-500" },
          { label: "Commandées", value: 3, color: "from-violet-500 to-purple-500" },
          { label: "Reçues", value: 5, color: "from-emerald-500 to-teal-500" },
        ].map((s, i) => (
          <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className={`p-2.5 rounded-xl bg-gradient-to-br ${s.color} w-fit mb-3`}><Package size={18} className="text-white" /></div>
            <p className="text-2xl font-bold text-gray-800">{s.value}</p>
            <p className="text-sm text-gray-500">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100"><div className="relative max-w-sm"><Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" /><input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm" /></div></div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50/50"><tr><th className="text-left px-6 py-3 font-semibold text-gray-600">Référence</th><th className="text-left px-6 py-3">Fournisseur</th><th className="text-left px-6 py-3">Date</th><th className="text-center px-6 py-3">Articles</th><th className="text-right px-6 py-3">Montant</th><th className="text-center px-6 py-3">Statut</th><th className="text-center px-6 py-3">Actions</th></tr></thead>
          <tbody>
            {orders.map((o, i) => {
              const s = statusCfg[o.status]
              return (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/30">
                  <td className="px-6 py-4 font-medium text-gray-800">{o.ref}</td>
                  <td className="px-6 py-4 text-gray-600">{o.supplier}</td>
                  <td className="px-6 py-4 text-gray-500">{o.date}</td>
                  <td className="px-6 py-4 text-center">{o.items}</td>
                  <td className="px-6 py-4 text-right font-semibold text-gray-800">{o.total}</td>
                  <td className="px-6 py-4 text-center"><span className={`px-2.5 py-1 rounded-full text-xs font-medium ${s.color}`}>{s.label}</span></td>
                  <td className="px-6 py-4"><div className="flex items-center justify-center gap-1"><button className="p-1.5 hover:bg-gray-100 rounded-lg"><Eye size={14} className="text-gray-400" /></button><button className="p-1.5 hover:bg-emerald-50 rounded-lg"><Check size={14} className="text-emerald-500" /></button><button className="p-1.5 hover:bg-red-50 rounded-lg"><X size={14} className="text-red-400" /></button></div></td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}