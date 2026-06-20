"use client"
import { useState } from "react"
import { Upload, FileText, Scan, Check, Loader2 } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function OCRPage() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)

  const handleFile = (e) => {
    const f = e.target.files?.[0]
    if (f) { setFile(f); setResult(null); const r = new FileReader(); r.onload = e => setPreview(e.target.result); r.readAsDataURL(f) }
  }

  const analyze = async () => {
    if (!file) return
    setAnalyzing(true)
    const token = localStorage.getItem("access_token")
    const fd = new FormData(); fd.append("image", file)
    try {
      const res = await fetch(API + "/ocr/invoice/", { method: "POST", headers: { Authorization: "Bearer " + token }, body: fd })
      const d = await res.json()
      setResult(d.data)
    } catch (e) { alert("Erreur analyse") }
    setAnalyzing(false)
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      <div><h1 className="text-2xl font-bold text-gray-800">OCR Factures</h1><p className="text-sm text-gray-500">Analysez automatiquement vos factures</p></div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border p-6">
          <h3 className="font-semibold flex items-center gap-2 mb-4"><Upload size={20} className="text-emerald-500" /> Télécharger</h3>
          <div className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer hover:border-emerald-300" onClick={() => document.getElementById("fileInput").click()}>
            <input id="fileInput" type="file" accept="image/*" className="hidden" onChange={handleFile} />
            {preview ? <div><img src={preview} className="max-h-48 mx-auto rounded-lg" /><p className="text-sm text-emerald-600 mt-2"><Check size={14} className="inline" /> {file?.name}</p></div>
            : <div><FileText size={48} className="mx-auto text-gray-300 mb-3" /><p className="text-sm text-gray-500">Déposez une facture (JPEG/PNG)</p></div>}
          </div>
          <button onClick={analyze} disabled={!file || analyzing} className="w-full mt-4 py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium disabled:opacity-50">
            {analyzing ? <Loader2 size={16} className="inline animate-spin mr-2" /> : <Scan size={16} className="inline mr-2" />} {analyzing ? "Analyse..." : "Analyser"}
          </button>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border p-6">
          <h3 className="font-semibold mb-4">Résultats</h3>
          {result ? (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-2"><div className="p-2 bg-gray-50 rounded"><span className="text-xs text-gray-500">N° Facture</span><p className="font-medium">{result.invoice_number||"N/A"}</p></div><div className="p-2 bg-gray-50 rounded"><span className="text-xs text-gray-500">Date</span><p className="font-medium">{result.date||"N/A"}</p></div></div>
              <div className="p-2 bg-gray-50 rounded"><span className="text-xs text-gray-500">Fournisseur</span><p className="font-medium">{result.supplier_name||"N/A"}</p></div>
              <div className="p-2 bg-gray-50 rounded"><span className="text-xs text-gray-500">Montant</span><p className="font-bold text-lg">{result.total_amount?.toLocaleString()} XAF</p></div>
              {result.items?.length > 0 && <div className="space-y-1"><p className="text-xs text-gray-500">Articles :</p>{result.items.map((it,i)=><p key={i} className="text-xs">• {it.description} x{it.quantity} @ {it.unit_price?.toLocaleString()}</p>)}</div>}
            </div>
          ) : <p className="text-gray-400 text-center py-8">Téléchargez une facture</p>}
        </div>
      </div>
    </div>
  )
}