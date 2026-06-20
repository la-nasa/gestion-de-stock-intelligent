"use client"
import { Package } from "lucide-react"

export function EmptyState({ message }) {
  return <div className="text-center py-12 text-gray-400"><Package size={48} className="mx-auto mb-3 opacity-30" /><p>{message || "Aucune donnée"}</p></div>
}
