"use client"
import { useState } from "react"
import { Search, Plus, FolderTree, Package, ChevronRight } from "lucide-react"

const categories = [
  { name: "Informatique", count: 45, children: [
    { name: "Ordinateurs", count: 12 }, { name: "Périphériques", count: 15 }, { name: "Réseau", count: 8 }, { name: "Consommables", count: 10 }
  ]},
  { name: "Bureautique", count: 32, children: [
    { name: "Fournitures", count: 18 }, { name: "Papeterie", count: 8 }, { name: "Mobilier", count: 6 }
  ]},
  { name: "Laboratoire", count: 18, children: [
    { name: "Équipements", count: 8 }, { name: "Produits chimiques", count: 6 }, { name: "Verrerie", count: 4 }
  ]},
  { name: "Génie Civil", count: 12 },
  { name: "Général", count: 25 },
]

export default function CategoriesPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Catégories</h1><p className="text-sm text-gray-500 mt-1">Gestion des catégories de produits</p></div>
        <button className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg transition-all"><Plus size={16} /> Nouvelle catégorie</button>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="relative max-w-sm mb-6">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input placeholder="Rechercher..." className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((cat, i) => (
            <div key={i} className="p-5 border border-gray-100 rounded-2xl hover:shadow-md hover:border-emerald-200 transition-all cursor-pointer group">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-sm">
                  <FolderTree size={18} className="text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">{cat.name}</h3>
                  <p className="text-xs text-gray-400">{cat.count} produits</p>
                </div>
              </div>
              {cat.children && (
                <div className="mt-3 pt-3 border-t border-gray-50 space-y-1.5">
                  {cat.children.map((child, j) => (
                    <div key={j} className="flex items-center justify-between text-sm py-1.5 px-3 rounded-lg hover:bg-gray-50 transition-colors">
                      <span className="text-gray-600">{child.name}</span>
                      <span className="text-xs text-gray-400">{child.count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}