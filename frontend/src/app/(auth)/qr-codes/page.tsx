"use client"
import { useState, useEffect } from "react"
import { QrCode, Download, Scan, Camera } from "lucide-react"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function QRCodesPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState("")
  const [qrImage, setQrImage] = useState(null)
  const [scanCode, setScanCode] = useState("")
  const [scanResult, setScanResult] = useState(null)

  useEffect(() => {
    fetch(API + "/products/", { headers: H() }).then(r => r.json()).then(d => {
      setProducts(d?.data?.results || d.data || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const generateQR = async () => {
    if (!selected) return
    try {
      const res = await fetch(API + "/products/" + selected + "/qr/generate/", { method: "POST", headers: H() })
      const d = await res.json()
      if (d.success) setQrImage(d.data?.image_url || null)
      if (d.data?.code) {
        const imgRes = await fetch(API + "/products/" + selected + "/codes/", { headers: H() })
        const imgData = await imgRes.json()
        setQrImage(imgData.data?.qr_code?.image_url || null)
      }
    } catch (e) { alert("Erreur génération") }
  }

  const scanQR = async () => {
    if (!scanCode) return
    try {
      const res = await fetch(API + "/qr/scan/", { method: "POST", headers: H(), body: JSON.stringify({ code: scanCode }) })
      const d = await res.json()
      setScanResult(d.success ? d.data : null)
    } catch (e) { alert("Erreur scan") }
  }

  const downloadQR = () => {
    if (qrImage) { const a = document.createElement("a"); a.href = qrImage; a.download = "qrcode.png"; a.click() }
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      <div><h1 className="text-2xl font-bold text-gray-800">QR Codes & Barcodes</h1><p className="text-sm text-gray-500">{products.length} produits disponibles</p></div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2"><QrCode size={20} className="text-emerald-500" /> Générer</h3>
          <SelectSearch apiUrl={API + "/products/"} value={selected} onChange={setSelected} placeholder="Sélectionner un produit..." />
          <button onClick={generateQR} className="w-full py-2.5 bg-emerald-500 text-white rounded-xl text-sm font-medium">Générer QR Code</button>
          {qrImage && (
            <div className="text-center p-4 bg-gray-50 rounded-xl">
              <img src={qrImage} alt="QR" className="mx-auto w-48 h-48 object-contain bg-white p-2 rounded-lg" />
              <button onClick={downloadQR} className="mt-3 px-4 py-1.5 text-xs bg-white border rounded-lg hover:bg-gray-50"><Download size={12} className="inline mr-1" /> Télécharger</button>
            </div>
          )}
        </div>
        <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2"><Scan size={20} className="text-blue-500" /> Scanner</h3>
          <input value={scanCode} onChange={e => setScanCode(e.target.value)} placeholder="Contenu du QR code..." className="w-full p-2.5 border rounded-xl text-sm" />
          <button onClick={scanQR} className="w-full py-2.5 bg-blue-500 text-white rounded-xl text-sm font-medium"><Camera size={16} className="inline mr-2" /> Scanner</button>
          {scanResult && (
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200">
              <p className="font-medium text-emerald-800">✓ {scanResult.product?.name}</p>
              <p className="text-xs text-gray-500">Réf: {scanResult.product?.reference} | SKU: {scanResult.product?.sku}</p>
              <p className="text-xs text-gray-500">Prix: {scanResult.product?.unit_price?.toLocaleString()} XAF</p>
              {scanResult.stocks?.map((s,i) => (
                <p key={i} className="text-xs text-gray-600">{s.warehouse}: {s.quantity} (disp: {s.available})</p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}