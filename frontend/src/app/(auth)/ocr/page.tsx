"use client"

import React, { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { toast } from "react-hot-toast"
import {
  Upload,
  FileText,
  Scan,
  Check,
  X,
  Package,
  Building2,
  Hash,
  Calendar,
  DollarSign,
  ShoppingCart,
  ArrowRight,
  Loader2,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { post } from "@/lib/api/client"

export default function OCRPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [creating, setCreating] = useState(false)

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const handleFile = (file: File) => {
    if (!file.type.startsWith("image/") && file.type !== "application/pdf") {
      toast.error("Format non supporté. Utilisez JPEG, PNG ou PDF.")
      return
    }
    setFile(file)
    setResult(null)
    
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target?.result as string)
    reader.readAsDataURL(file)
  }

  const handleAnalyze = async () => {
    if (!file) {
      toast.error("Veuillez sélectionner une facture")
      return
    }

    try {
      setAnalyzing(true)
      const formData = new FormData()
      formData.append("image", file)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ocr/invoice/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: formData,
        }
      )

      if (!response.ok) throw new Error("Erreur analyse")

      const data = await response.json()
      setResult(data.data)
      toast.success("Facture analysée !")
    } catch (error: any) {
      toast.error(error.message || "Erreur lors de l'analyse")
    } finally {
      setAnalyzing(false)
    }
  }

  const handleCreateEntry = async () => {
    if (!result) return

    try {
      setCreating(true)
      await post("/ocr/create-entry/", {
        supplier_id: result.supplier_id || result.matches?.suppliers?.[0]?.id,
        items: (result.items || []).map((item: any) => ({
          product_id: item.matches?.[0]?.id || item.product_id,
          quantity: item.quantity || 1,
          unit_price: item.unit_price || 0,
        })),
        invoice_number: result.invoice_number,
        date: result.date,
        warehouse_id: prompt("ID de l'entrepôt de réception:"),
      })

      toast.success("Entrée de stock créée !")
      router.push("/stocks/entries")
    } catch (error: any) {
      toast.error("Erreur création entrée")
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">OCR Factures</h1>
        <p className="text-sm text-gray-500 mt-1">
          Analysez automatiquement vos factures fournisseurs
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary-500" />
              Télécharger une facture
            </CardTitle>
            <CardDescription>
              Déposez une image ou un PDF de facture
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Zone de drop */}
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer",
                preview
                  ? "border-green-300 bg-green-50"
                  : "border-gray-300 hover:border-primary-300 hover:bg-primary-50/30"
              )}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              <input
                id="file-input"
                type="file"
                accept="image/*,application/pdf"
                className="hidden"
                onChange={handleFileSelect}
              />
              
              {preview ? (
                <div className="space-y-3">
                  <img
                    src={preview}
                    alt="Aperçu"
                    className="max-h-48 mx-auto rounded-lg shadow-sm"
                  />
                  <p className="text-sm text-green-600 font-medium">
                    <Check className="h-4 w-4 inline mr-1" />
                    {file?.name}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto">
                    <FileText className="h-6 w-6 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Déposez votre facture ici
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      JPEG, PNG ou PDF - Max 10 Mo
                    </p>
                  </div>
                </div>
              )}
            </div>

            <Button
              className="w-full mt-4"
              onClick={handleAnalyze}
              loading={analyzing}
              disabled={!file}
            >
              <Scan className="h-4 w-4 mr-2" />
              {analyzing ? "Analyse en cours..." : "Analyser la facture"}
            </Button>
          </CardContent>
        </Card>

        {/* Résultats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary-500" />
              Résultats de l'analyse
            </CardTitle>
            <CardDescription>
              Données extraites automatiquement
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analyzing ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="h-8 w-8 text-primary-500 animate-spin mb-4" />
                <p className="text-sm text-gray-500">Analyse de la facture...</p>
              </div>
            ) : result ? (
              <div className="space-y-4">
                {/* Infos facture */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                      <Hash className="h-3 w-3" />
                      N° Facture
                    </div>
                    <p className="text-sm font-medium">
                      {result.invoice_number || "Non détecté"}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                      <Calendar className="h-3 w-3" />
                      Date
                    </div>
                    <p className="text-sm font-medium">
                      {result.date || "Non détectée"}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                      <Building2 className="h-3 w-3" />
                      Fournisseur
                    </div>
                    <p className="text-sm font-medium">
                      {result.supplier_name || "Non détecté"}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                      <DollarSign className="h-3 w-3" />
                      Montant total
                    </div>
                    <p className="text-sm font-medium">
                      {result.total_amount
                        ? `${result.total_amount.toLocaleString()} XAF`
                        : "Non détecté"}
                    </p>
                  </div>
                </div>

                {/* Articles */}
                {result.items?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <ShoppingCart className="h-4 w-4" />
                      Articles détectés ({result.items.length})
                    </p>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {result.items.map((item: any, idx: number) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded-lg text-sm"
                        >
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 truncate">
                              {item.description || `Article ${idx + 1}`}
                            </p>
                            <p className="text-xs text-gray-500">
                              Qté: {item.quantity || "?"} ×{" "}
                              {item.unit_price?.toLocaleString() || "?"} XAF
                            </p>
                          </div>
                          {item.matches?.length > 0 && (
                            <Badge variant="success" className="ml-2 text-xs">
                              <Check className="h-3 w-3 mr-1" />
                              Trouvé
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Confiance */}
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <p>Confiance :</p>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        "h-full rounded-full",
                        (result.confidence || 0) > 0.7
                          ? "bg-green-500"
                          : (result.confidence || 0) > 0.4
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      )}
                      style={{
                        width: `${((result.confidence || 0) * 100)}%`,
                      }}
                    />
                  </div>
                  <span>{Math.round((result.confidence || 0) * 100)}%</span>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setFile(null)
                      setPreview(null)
                      setResult(null)
                    }}
                  >
                    <X className="h-4 w-4 mr-1" />
                    Réinitialiser
                  </Button>
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={handleCreateEntry}
                    loading={creating}
                    disabled={!result.items?.length}
                  >
                    <Package className="h-4 w-4 mr-1" />
                    Créer l'entrée de stock
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                <Scan className="h-12 w-12 mb-3 opacity-30" />
                <p className="text-sm">Téléchargez une facture pour voir les résultats</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}