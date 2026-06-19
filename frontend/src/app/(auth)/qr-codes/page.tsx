"use client"

import React, { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { toast } from "react-hot-toast"
import {
  QrCode,
  Barcode,
  Printer,
  Scan,
  Search,
  Download,
  Copy,
  Check,
  Camera,
} from "lucide-react"
import { post, get } from "@/lib/api/client"
import { cn } from "@/lib/utils"

export default function QRCodesPage() {
  const [productId, setProductId] = useState("")
  const [qrImage, setQrImage] = useState<string | null>(null)
  const [barcodeImage, setBarcodeImage] = useState<string | null>(null)
  const [productInfo, setProductInfo] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [scanCode, setScanCode] = useState("")
  const [scanResult, setScanResult] = useState<any>(null)
  const [copied, setCopied] = useState(false)

  const handleGenerateQR = async () => {
    if (!productId) {
      toast.error("Veuillez entrer un ID produit")
      return
    }
    try {
      setLoading(true)
      const response = await post<{ data: any }>(`/products/${productId}/qr/generate/`)
      setQrImage(response.data.image_url)
      toast.success("QR code généré !")
    } catch (error: any) {
      toast.error(error.response?.data?.message || "Erreur génération")
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateBarcode = async () => {
    if (!productId) {
      toast.error("Veuillez entrer un ID produit")
      return
    }
    try {
      setLoading(true)
      const response = await post<{ data: any }>(
        `/products/${productId}/barcode/generate/`,
        { format: "CODE128" }
      )
      setBarcodeImage(response.data.image_url)
      toast.success("Code-barres généré !")
    } catch (error: any) {
      toast.error(error.response?.data?.message || "Erreur génération")
    } finally {
      setLoading(false)
    }
  }

  const handleScan = async () => {
    if (!scanCode) {
      toast.error("Veuillez entrer un code QR")
      return
    }
    try {
      setLoading(true)
      const response = await post<{ data: any }>("/qr/scan/", { code: scanCode })
      setScanResult(response.data)
      toast.success("Produit trouvé !")
    } catch (error: any) {
      toast.error("Produit non trouvé")
      setScanResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    toast.success("Code copié !")
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">QR Codes & Barcodes</h1>
        <p className="text-sm text-gray-500 mt-1">
          Générez et scannez des QR codes pour vos produits
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Génération */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <QrCode className="h-5 w-5 text-primary-500" />
              Générer un QR Code / Barcode
            </CardTitle>
            <CardDescription>
              Entrez l'ID d'un produit pour générer ses codes
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="ID du produit (UUID)"
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                className="flex-1"
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleGenerateQR} loading={loading} className="flex-1">
                <QrCode className="h-4 w-4 mr-2" />
                QR Code
              </Button>
              <Button onClick={handleGenerateBarcode} loading={loading} variant="outline" className="flex-1">
                <Barcode className="h-4 w-4 mr-2" />
                Code-barres
              </Button>
            </div>

            {/* Aperçu QR */}
            {qrImage && (
              <div className="mt-4 p-4 bg-gray-50 rounded-xl text-center">
                <p className="text-xs font-medium text-gray-500 mb-3">QR Code généré</p>
                <img
                  src={qrImage}
                  alt="QR Code"
                  className="mx-auto w-48 h-48 object-contain bg-white p-2 rounded-lg shadow-sm"
                />
                <div className="flex gap-2 mt-3 justify-center">
                  <Button size="sm" variant="outline" onClick={() => window.open(qrImage, '_blank')}>
                    <Download className="h-3 w-3 mr-1" />
                    Télécharger
                  </Button>
                  <Button size="sm" variant="outline">
                    <Printer className="h-3 w-3 mr-1" />
                    Imprimer
                  </Button>
                </div>
              </div>
            )}

            {/* Aperçu Barcode */}
            {barcodeImage && (
              <div className="mt-4 p-4 bg-gray-50 rounded-xl text-center">
                <p className="text-xs font-medium text-gray-500 mb-3">Code-barres généré</p>
                <img
                  src={barcodeImage}
                  alt="Code-barres"
                  className="mx-auto max-w-full h-24 object-contain bg-white p-2 rounded-lg shadow-sm"
                />
                <div className="flex gap-2 mt-3 justify-center">
                  <Button size="sm" variant="outline" onClick={() => window.open(barcodeImage, '_blank')}>
                    <Download className="h-3 w-3 mr-1" />
                    Télécharger
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Scanner */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Scan className="h-5 w-5 text-primary-500" />
              Scanner un QR Code
            </CardTitle>
            <CardDescription>
              Entrez le contenu d'un QR code pour retrouver le produit
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Contenu du QR code scanné..."
                value={scanCode}
                onChange={(e) => setScanCode(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleScan} loading={loading}>
                <Camera className="h-4 w-4 mr-2" />
                Scanner
              </Button>
            </div>

            {/* Résultat scan */}
            {scanResult && (
              <div className="mt-4 p-4 bg-green-50 rounded-xl border border-green-200">
                <p className="text-sm font-medium text-green-800 mb-3">
                  ✓ Produit trouvé
                </p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Nom :</span>
                    <span className="text-sm font-medium">{scanResult.product.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Référence :</span>
                    <span className="text-sm font-medium">{scanResult.product.reference}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">SKU :</span>
                    <span className="text-sm font-medium">{scanResult.product.sku}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Prix :</span>
                    <span className="text-sm font-medium">
                      {scanResult.product.unit_price?.toLocaleString()} XAF
                    </span>
                  </div>
                  
                  {/* Stocks */}
                  {scanResult.stocks?.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-green-200">
                      <p className="text-xs font-medium text-gray-500 mb-2">Stocks :</p>
                      {scanResult.stocks.map((stock: any, idx: number) => (
                        <div key={idx} className="flex justify-between text-xs">
                          <span>{stock.warehouse}</span>
                          <span className="font-medium">{stock.quantity} ({stock.available} disp.)</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}