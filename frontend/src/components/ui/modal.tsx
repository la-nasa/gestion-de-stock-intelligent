"use client"
import { useState } from "react"
import { X } from "lucide-react"

export function Modal({ open, onClose, title, children }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-lg mx-4 animate-scale-in">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-800">{title}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg"><X size={20} /></button>
        </div>
        {children}
      </div>
    </div>
  )
}
