"use client"
import { useState } from "react"
import { Calendar, Clock, Plus, ToggleLeft, ToggleRight } from "lucide-react"
import { Modal } from "@/components/ui/modal"

export default function ScheduledReportsPage() {
  const [schedules, setSchedules] = useState([
    { id: 1, name: "Rapport stock quotidien", type: "Niveau de stock", frequency: "Quotidien", time: "08:00", active: true },
    { id: 2, name: "Rapport consommation mensuel", type: "Consommation", frequency: "Mensuel", time: "06:00", active: true },
    { id: 3, name: "Rapport inventaire hebdo", type: "Inventaire", frequency: "Hebdomadaire", time: "18:00", active: false },
  ])
  const [show, setShow] = useState(false)
  const [form, setForm] = useState({ name: "", type: "stock_level", frequency: "Quotidien", time: "08:00" })

  const toggle = (id) => setSchedules(schedules.map(s => s.id === id ? {...s, active: !s.active} : s))
  const create = () => { setSchedules([...schedules, {...form, id: Date.now(), active: true}]); setShow(false) }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Rapports planifiés</h1><p className="text-sm text-gray-500">{schedules.length} planification(s)</p></div>
        <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvelle planification</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {schedules.map(s => (
          <div key={s.id} className="bg-white rounded-2xl p-5 shadow-sm border">
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-lg" style={{background: s.active ? "#0d948815" : "#6b728015"}}><Clock size={18} style={{color: s.active ? "#0d9488" : "#6b7280"}} /></div>
              <button onClick={() => toggle(s.id)}>{s.active ? <ToggleRight size={20} className="text-emerald-500" /> : <ToggleLeft size={20} className="text-gray-400" />}</button>
            </div>
            <h3 className="font-semibold text-gray-800">{s.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{s.type}</p>
            <div className="mt-3 pt-3 border-t space-y-1 text-xs text-gray-500">
              <div className="flex items-center gap-1"><Calendar size={12} /> {s.frequency}</div>
              <div className="flex items-center gap-1"><Clock size={12} /> À {s.time}</div>
            </div>
          </div>
        ))}
      </div>
      <Modal open={show} onClose={() => setShow(false)} title="Nouvelle planification">
        <div className="space-y-3">
          <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Nom du rapport" className="w-full p-2.5 border rounded-xl text-sm" />
          <select value={form.type} onChange={e => setForm({...form, type: e.target.value})} className="w-full p-2.5 border rounded-xl text-sm">
            <option value="stock_level">Niveau de stock</option><option value="movements">Mouvements</option><option value="consumption">Consommation</option><option value="inventory">Inventaire</option>
          </select>
          <div className="grid grid-cols-2 gap-3">
            <select value={form.frequency} onChange={e => setForm({...form, frequency: e.target.value})} className="p-2.5 border rounded-xl text-sm">
              <option>Quotidien</option><option>Hebdomadaire</option><option>Mensuel</option>
            </select>
            <input type="time" value={form.time} onChange={e => setForm({...form, time: e.target.value})} className="p-2.5 border rounded-xl text-sm" />
          </div>
          <button onClick={create} className="w-full py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer</button>
        </div>
      </Modal>
    </div>
  )
}