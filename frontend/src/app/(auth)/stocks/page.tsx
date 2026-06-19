"use client"
import { useState } from "react"
import { Search, Package, TrendingUp, TrendingDown, AlertTriangle, ArrowUpDown } from "lucide-react"

const stocks = [
  { product: "Ordinateur Dell Latitude", ref: "DELL-LAT-5540", warehouse: "Entrepôt Central", qty: 45, available: 42, price: "450 000", value: "20 250 000", status: "normal" },
  { product: "Imprimante HP LaserJet", ref: "HP-LJ-MFP4101", warehouse: "Magasin Informatique", qty: 8, available: 6, price: "180 000", value: "1 440 000", status: "low" },
  { product: "Papier A4 80g", ref: "PAP-A4-80", warehouse: "Magasin Fournitures", qty: 520, available: 500, price: "2 500", value: "1 300 000", status: "normal" },
  { product: "Projecteur Epson", ref: "EPS-EBX51", warehouse: "Entrepôt Central", qty: 2, available: 0, price: "300 000", value: "600 000", status: "out" },
  { product: "Microscope Olympus", ref: "OLY-CX23", warehouse: "Entrepôt Bonabéri", qty: 6, available: 5, price: "500 000", value: "3 000 000", status: "normal" },
]

export default function StocksPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Stocks</h1><p className="text-sm text-gray-500 mt-1">Vue d'ensemble des stocks par entrepôt</p></div>
        <button className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><ArrowUpDown size={16} /> Transfert</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Articles en stock", value: stocks.length, icon: Package, color: "from-emerald-500 to-teal-500" },
          { label: "Valeur totale", value: "26.6M XAF", icon: TrendingUp, color: "from-blue-500 to-indigo-500" },
          { label: "Stocks bas", value: "3", icon: AlertTriangle, color: "from-amber-500 to-orange-500" },
          { label: "Ruptures", value: "1", icon: TrendingDown, color: "from-rose-500 to-red-500" },
        ].map((s, i) => {
          const Icon = s.icon
          return (
            <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2.5 rounded-xl bg-gradient-to-br ${s.color} shadow-sm`}><Icon size={18} className="text-white" /></div>
              </div>
              <p className="text-2xl font-bold text-gray-800">{s.value}</p>
              <p className="text-sm text-gray-500">{s.label}</p>
            </div>
          )
        })}
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <div className="relative max-w-sm">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm" />
          </div>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50/50">
            <tr>
              <th className="text-left px-6 py-3 font-semibold text-gray-600">Produit</th>
              <th className="text-left px-6 py-3 font-semibold text-gray-600">Entrepôt</th>
              <th className="text-center px-6 py-3 font-semibold text-gray-600">Qté</th>
              <th className="text-center px-6 py-3 font-semibold text-gray-600">Disponible</th>
              <th className="text-right px-6 py-3 font-semibold text-gray-600">Prix Unit.</th>
              <th className="text-right px-6 py-3 font-semibold text-gray-600">Valeur</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((s, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/30">
                <td className="px-6 py-4"><p className="font-medium text-gray-800">{s.product}</p><p className="text-xs text-gray-400">{s.ref}</p></td>
                <td className="px-6 py-4"><span className="px-2 py-1 rounded-full text-xs bg-blue-50 text-blue-700">{s.warehouse}</span></td>
                <td className="px-6 py-4 text-center">
                  <span className={`font-semibold ${s.status==="out"?"text-red-600":s.status==="low"?"text-amber-600":"text-emerald-600"}`}>{s.qty}</span>
                </td>
                <td className="px-6 py-4 text-center font-medium">{s.available}</td>
                <td className="px-6 py-4 text-right text-gray-600">{s.price} XAF</td>
                <td className="px-6 py-4 text-right font-semibold text-gray-800">{s.value} XAF</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}