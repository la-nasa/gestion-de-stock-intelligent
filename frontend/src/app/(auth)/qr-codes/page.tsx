"use client"
import { useState, useEffect } from "react"
import { QrCode, Download, Scan, Camera, Copy, Check } from "lucide-react"
import { SelectSearch } from "@/components/ui/select-search"
import { Loading } from "@/components/features/loading"

const API = "http://localhost:8000/api/v1"
const token = () => typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
const H = (m) => ({ "Content-Type": "application/json", Authorization: "Bearer " + token(), ...m })

export default function QRCodesPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState("")
  const [qrData, setQrData] = useState(null)
  const [scanCode, setScanCode] = useState("")
  const [scanResult, setScanResult] = useState(null)
  const [copied, setCopied] = useState(false)

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
      if (d.success) {
        setQrData(d.data)
      }
    } catch (e) { alert("Erreur génération: " + e.message) }
  }

  const scanQR = async () => {
    if (!scanCode) return
    try {
      const res = await fetch(API + "/qr/scan/", { method: "POST", headers: H(), body: JSON.stringify({ code: scanCode }) })
      const d = await res.json()
      setScanResult(d.success ? d.data : null)
    } catch (e) { alert("Erreur scan: " + e.message) }
  }

  const copyCode = () => {
    if (qrData?.code) {
      navigator.clipboard.writeText(qrData.code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (loading) return <Loading />

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">QR Codes & Barcodes</h1>
        <p className="text-sm text-gray-500 mt-1">{products.length} produits disponibles</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Génération */}
        <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <QrCode size={22} className="text-emerald-500" />
            Générer un QR Code
          </h3>
          <p className="text-sm text-gray-500">Sélectionnez un produit pour générer son QR code</p>
          <SelectSearch 
            apiUrl={API + "/products/"} 
            value={selected} 
            onChange={setSelected} 
            placeholder="Sélectionner un produit..." 
          />
          <button 
            onClick={generateQR} 
            disabled={!selected}
            className="w-full py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl text-sm font-medium hover:shadow-lg disabled:opacity-50 transition-all"
          >
            <QrCode size={16} className="inline mr-2" />
            Générer le QR Code
          </button>

          {qrData && (
            <div className="mt-4 p-5 bg-gray-50 rounded-xl border border-gray-200 text-center">
              <div className="bg-white p-4 rounded-lg inline-block mb-3">
                <QrCode size={120} className="text-gray-800 mx-auto" />
              </div>
              <p className="text-sm font-medium text-gray-700 mb-1">
                QR Code pour : <span className="text-emerald-600">{products.find(p => p.id === selected)?.name || "Produit"}</span>
              </p>
              <p className="text-xs text-gray-400 mb-3 break-all">Code: {qrData.code?.substring(0, 80)}...</p>
              <div className="flex gap-2 justify-center">
                <button 
                  onClick={copyCode}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs border border-gray-300 rounded-lg hover:bg-white transition-colors"
                >
                  {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                  {copied ? "Copié !" : "Copier le code"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Scanner */}
        <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Scan size={22} className="text-blue-500" />
            Scanner un QR Code
          </h3>
          <p className="text-sm text-gray-500">Entrez le contenu d'un QR code pour retrouver le produit</p>
          <div className="flex gap-2">
            <input 
              value={scanCode} 
              onChange={e => setScanCode(e.target.value)} 
              onKeyDown={e => e.key === "Enter" && scanQR()}
              placeholder="Collez le contenu du QR code..." 
              className="flex-1 p-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20"
            />
            <button 
              onClick={scanQR} 
              disabled={!scanCode}
              className="px-5 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl text-sm font-medium hover:shadow-lg disabled:opacity-50 transition-all"
            >
              <Camera size={16} className="inline mr-1" />
              Scanner
            </button>
          </div>

          {scanResult && (
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200">
              <div className="flex items-center gap-2 mb-2">
                <Check size={18} className="text-emerald-600" />
                <span className="font-medium text-emerald-800">Produit trouvé !</span>
              </div>
              <div className="space-y-1.5 text-sm">
                <p><strong>Nom :</strong> {scanResult.product?.name}</p>
                <p><strong>Référence :</strong> {scanResult.product?.reference}</p>
                <p><strong>SKU :</strong> {scanResult.product?.sku}</p>
                <p><strong>Prix :</strong> {scanResult.product?.unit_price?.toLocaleString()} XAF</p>
                {scanResult.stocks && scanResult.stocks.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-emerald-200">
                    <p className="font-medium text-xs text-gray-500 mb-1">Stocks :</p>
                    {scanResult.stocks.map((s, i) => (
                      <p key={i} className="text-xs text-gray-600">
                        {s.warehouse} : {s.quantity} (disponible: {s.available})
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {scanResult === null && scanCode && (
            <div className="p-4 bg-red-50 rounded-xl border border-red-200">
              <p className="text-sm text-red-600">❌ Produit non trouvé pour ce code</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
