"use client"
import { useState, useEffect } from "react"
import { Plus, Download, Eye, Trash2 } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function InventoriesPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const [detail, setDetail] = useState(null)
  const [wid, setWid] = useState("")

  const fetchData = () => {
    fetch(API + "/inventories/", { headers: H() }).then(r => r.json()).then(d => {
      setData(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { fetchData() }, [])

  const create = async () => {
    if (!wid) return alert("Sélectionnez un entrepôt")
    await fetch(API + "/inventories/", { method: "POST", headers: H(), body: JSON.stringify({ warehouse_id: wid, type: "FULL" }) })
    setShow(false); fetchData()
  }
  const del = async (id) => { if (confirm("Supprimer ?")) { await fetch(API + "/inventories/" + id + "/", { method: "DELETE", headers: H() }); fetchData() } }
  const viewDetail = async (id) => {
    const r = await fetch(API + "/inventories/" + id + "/", { headers: H() })
    const d = await r.json()
    setDetail(d.data || d)
  }

  const exp = () => {
    const csv = "Réf,Entrepôt,Date,Articles,Écarts,Statut\n" + data.map(i => [i.reference,i.warehouse_name,i.start_date,i.counted_items+"/"+i.expected_items,i.differences,i.status].join(",")).join("\n")
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\uFEFF"+csv])); a.download = "inventaires.csv"; a.click()
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-gray-800">Inventaires</h1><p className="text-sm text-gray-500">{data.length} inventaire(s)</p></div>
        <div className="flex gap-2">
          <button onClick={exp} className="flex items-center gap-2 px-4 py-2.5 text-sm border rounded-xl hover:bg-gray-50"><Download size={16} /> Export</button>
          <button onClick={() => setShow(true)} className="flex items-center gap-2 px-5 py-2.5 text-sm text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg"><Plus size={16} /> Nouvel inventaire</button>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-gray-50"><tr><th className="text-left px-6 py-3">Réf</th><th className="text-left px-6 py-3">Entrepôt</th><th className="text-center px-6 py-3">Articles</th><th className="text-center px-6 py-3">Écarts</th><th className="text-right px-6 py-3">Écart valeur</th><th className="text-center px-6 py-3">Statut</th><th className="text-center px-6 py-3"></th></tr></thead>
        <tbody>{data.map(i => (<tr key={i.id} className="border-b hover:bg-gray-50/30"><td className="px-6 py-4 font-medium">{i.reference}</td><td className="px-6 py-4">{i.warehouse_name}</td><td className="px-6 py-4 text-center">{i.counted_items}/{i.expected_items}</td><td className="px-6 py-4 text-center"><span className={i.differences===0?"text-emerald-600":"text-red-600"}>{i.differences}</span></td><td className="px-6 py-4 text-right font-medium">{i.value_difference?.toLocaleString()} XAF</td><td className="px-6 py-4 text-center">{i.status}</td><td className="px-6 py-4"><div className="flex justify-center gap-1"><button onClick={() => viewDetail(i.id)} className="p-1 hover:bg-gray-100 rounded"><Eye size={14} /></button><button onClick={() => del(i.id)} className="p-1 hover:bg-red-50 rounded"><Trash2 size={14} className="text-red-400" /></button></div></td></tr>))}</tbody></table>
      </div>

      <Modal open={show} onClose={() => setShow(false)} title="Nouvel inventaire">
        <div className="space-y-3">
          <SelectSearch apiUrl={API + "/stocks/"} value={wid} onChange={setWid} labelField="warehouse_name" valueField="warehouse" placeholder="Entrepôt *" />
          <button onClick={create} className="w-full py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium">Créer l'inventaire</button>
        </div>
      </Modal>

      {detail && (
        <Modal open={!!detail} onClose={() => setDetail(null)} title={"Détail " + detail.reference}>
          <div className="space-y-2 text-sm">
            <p><strong>Entrepôt:</strong> {detail.warehouse_name}</p>
            <p><strong>Articles:</strong> {detail.counted_items}/{detail.expected_items}</p>
            <p><strong>Écarts:</strong> {detail.differences} | Valeur: {detail.value_difference?.toLocaleString()} XAF</p>
            {detail.lines?.length > 0 && (
              <div className="mt-3 max-h-60 overflow-y-auto">
                <table className="w-full text-xs"><thead><tr><th className="text-left">Produit</th><th className="text-right">Attendu</th><th className="text-right">Compté</th><th className="text-right">Écart</th></tr></thead>
                <tbody>{detail.lines.map((l,i) => (<tr key={i} className="border-t"><td className="py-1">{l.product_name}</td><td className="text-right">{l.expected_quantity}</td><td className="text-right">{l.counted_quantity||"-"}</td><td className="text-right">{l.difference||0}</td></tr>))}</tbody></table>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}