"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { toast } from "react-hot-toast"
import {
  FileText,
  Download,
  FileSpreadsheet,
  FileDown,
  Package,
  ArrowUpDown,
  TrendingUp,
  ClipboardList,
  Calendar,
  Filter,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { post } from "@/lib/api/client"

const reportTypes = [
  {
    id: "stock_level",
    name: "Niveau de stock",
    description: "État actuel des stocks par entrepôt et catégorie",
    icon: Package,
    color: "bg-blue-50 text-blue-600",
  },
  {
    id: "movements",
    name: "Mouvements de stock",
    description: "Historique des entrées, sorties et transferts",
    icon: ArrowUpDown,
    color: "bg-green-50 text-green-600",
  },
  {
    id: "consumption",
    name: "Consommation par département",
    description: "Analyse de la consommation par département",
    icon: TrendingUp,
    color: "bg-yellow-50 text-yellow-600",
  },
  {
    id: "inventory",
    name: "Rapport d'inventaire",
    description: "Résultats détaillés d'une session d'inventaire",
    icon: ClipboardList,
    color: "bg-purple-50 text-purple-600",
  },
]

const formats = [
  { id: "PDF", name: "PDF", icon: FileText, color: "bg-red-50 text-red-600 border-red-200" },
  { id: "EXCEL", name: "Excel", icon: FileSpreadsheet, color: "bg-green-50 text-green-600 border-green-200" },
  { id: "CSV", name: "CSV", icon: FileDown, color: "bg-blue-50 text-blue-600 border-blue-200" },
]

export default function ReportsPage() {
  const router = useRouter()
  const [selectedType, setSelectedType] = useState("stock_level")
  const [selectedFormat, setSelectedFormat] = useState("PDF")
  const [generating, setGenerating] = useState(false)
  const [filters, setFilters] = useState({
    date_from: "",
    date_to: "",
  })

  const handleGenerate = async () => {
    try {
      setGenerating(true)
      const payload: any = {
        type: selectedType,
        format: selectedFormat,
        filters: {},
      }

      if (filters.date_from) payload.filters.date_from = filters.date_from
      if (filters.date_to) payload.filters.date_to = filters.date_to

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reports/generate/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify(payload),
        }
      )

      if (!response.ok) throw new Error("Erreur lors de la génération")

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `rapport_${selectedType}.${selectedFormat.toLowerCase()}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success("Rapport généré avec succès !")
    } catch (error: any) {
      toast.error(error.message || "Erreur lors de la génération")
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Rapports</h1>
        <p className="text-sm text-gray-500 mt-1">
          Générez des rapports dans différents formats
        </p>
      </div>

      {/* Type de rapport */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          Type de rapport
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {reportTypes.map((type) => {
            const Icon = type.icon
            return (
              <Card
                key={type.id}
                className={cn(
                  "cursor-pointer transition-all hover:shadow-soft-md",
                  selectedType === type.id
                    ? "ring-2 ring-primary-500 border-primary-200"
                    : "border-gray-200"
                )}
                onClick={() => setSelectedType(type.id)}
              >
                <CardContent className="p-4 flex items-start gap-4">
                  <div className={cn("p-2.5 rounded-lg", type.color)}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{type.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {type.description}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Filtres */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filtres</CardTitle>
          <CardDescription>
            Filtrez les données du rapport (optionnel)
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Date de début"
            type="date"
            value={filters.date_from}
            onChange={(e) =>
              setFilters({ ...filters, date_from: e.target.value })
            }
          />
          <Input
            label="Date de fin"
            type="date"
            value={filters.date_to}
            onChange={(e) =>
              setFilters({ ...filters, date_to: e.target.value })
            }
          />
        </CardContent>
      </Card>

      {/* Format */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          Format de sortie
        </h2>
        <div className="flex gap-3">
          {formats.map((format) => {
            const Icon = format.icon
            return (
              <button
                key={format.id}
                onClick={() => setSelectedFormat(format.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-3 rounded-lg border-2 transition-all",
                  selectedFormat === format.id
                    ? format.color + " border-current"
                    : "border-gray-200 text-gray-500 hover:border-gray-300"
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium text-sm">{format.name}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Générer */}
      <div className="flex justify-end">
        <Button size="lg" onClick={handleGenerate} loading={generating}>
          <Download className="h-5 w-5 mr-2" />
          Générer le rapport
        </Button>
      </div>
    </div>
  )
}