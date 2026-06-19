"use client"

import React, { useState, useEffect, useCallback } from "react"
import { useRouter, useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  ArrowLeft,
  Save,
  CheckCircle,
  Play,
  Search,
  Package,
  AlertTriangle,
} from "lucide-react"
import { formatCurrency, formatDate, cn } from "@/lib/utils"
import { get, patch, post } from "@/lib/api/client"

interface InventoryLine {
  id: string
  product: string
  product_name: string
  product_reference: string
  expected_quantity: number
  counted_quantity: number | null
  difference: number
  unit_price: number
  difference_value: number
  counted_by_name: string | null
  counted_at: string | null
  notes: string
}

interface Inventory {
  id: string
  reference: string
  type: string
  status: string
  warehouse_name: string
  start_date: string
  supervisor_name: string
  expected_items: number
  counted_items: number
  differences: number
  total_value_expected: number
  total_value_counted: number
  value_difference: number
  lines: InventoryLine[]
}

export default function InventoryDetailPage() {
  const router = useRouter()
  const params = useParams()
  const [inventory, setInventory] = useState<Inventory | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState("")
  const [editingLine, setEditingLine] = useState<string | null>(null)
  const [editValue, setEditValue] = useState("")

  const fetchInventory = useCallback(async () => {
    try {
      setLoading(true)
      const response = await get<{ data: Inventory }>(`/inventories/${params.id}/`)
      setInventory(response.data)
    } catch (error) {
      console.error("Erreur chargement inventaire:", error)
    } finally {
      setLoading(false)
    }
  }, [params.id])

  useEffect(() => {
    fetchInventory()
  }, [fetchInventory])

  const handleStartCounting = async (lineId: string) => {
    setEditingLine(lineId)
    const line = inventory?.lines.find((l) => l.id === lineId)
    setEditValue(line?.counted_quantity?.toString() || "")
  }

  const handleSaveCount = async (lineId: string) => {
    try {
      setSaving(true)
      await patch(`/inventories/${params.id}/lines/${lineId}/`, {
        counted_quantity: parseInt(editValue),
        counted_at: new Date().toISOString(),
      })
      await fetchInventory()
      setEditingLine(null)
    } catch (error) {
      console.error("Erreur sauvegarde comptage:", error)
    } finally {
      setSaving(false)
    }
  }

  const handleValidate = async () => {
    if (confirm("Valider cet inventaire ? Cette action est irréversible.")) {
      try {
        await post(`/inventories/${params.id}/validate/`)
        await fetchInventory()
      } catch (error) {
        console.error("Erreur validation:", error)
      }
    }
  }

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="skeleton h-8 w-64" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-24" />
          ))}
        </div>
        <div className="skeleton h-96" />
      </div>
    )
  }

  if (!inventory) {
    return (
      <div className="text-center py-12">
        <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900">Inventaire introuvable</h3>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => router.push("/inventories")}
        >
          Retour à la liste
        </Button>
      </div>
    )
  }

  const progressPct = inventory.expected_items > 0
    ? Math.round((inventory.counted_items / inventory.expected_items) * 100)
    : 0

  const filteredLines = inventory.lines.filter(
    (line) =>
      line.product_name.toLowerCase().includes(search.toLowerCase()) ||
      line.product_reference.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {inventory.reference}
            </h1>
            <p className="text-sm text-gray-500">
              {inventory.warehouse_name} • {formatDate(inventory.start_date)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {inventory.status === "IN_PROGRESS" && (
            <Button onClick={handleValidate}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Valider l'inventaire
            </Button>
          )}
          {inventory.status === "PLANNED" && (
            <Button onClick={() => post(`/inventories/${params.id}/start/`).then(fetchInventory)}>
              <Play className="h-4 w-4 mr-2" />
              Démarrer l'inventaire
            </Button>
          )}
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{progressPct}%</p>
            <p className="text-xs text-gray-500">Progression</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{inventory.expected_items}</p>
            <p className="text-xs text-gray-500">Articles attendus</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{inventory.counted_items}</p>
            <p className="text-xs text-gray-500">Articles comptés</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className={cn(
              "text-2xl font-bold",
              inventory.differences === 0 ? "text-green-600" : "text-red-600"
            )}>
              {inventory.differences}
            </p>
            <p className="text-xs text-gray-500">Écarts</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className={cn(
              "text-2xl font-bold",
              inventory.value_difference === 0 ? "text-green-600" : "text-red-600"
            )}>
              {formatCurrency(inventory.value_difference)}
            </p>
            <p className="text-xs text-gray-500">Écart valeur</p>
          </CardContent>
        </Card>
      </div>

      {/* Barre de progression */}
      <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            progressPct >= 100 ? "bg-green-500" : "bg-blue-500"
          )}
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Recherche */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Rechercher un article..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Lignes d'inventaire */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table-premium">
            <thead>
              <tr>
                <th>Produit</th>
                <th className="text-right">Attendu</th>
                <th className="text-right">Compté</th>
                <th className="text-right">Écart</th>
                <th className="text-right">Valeur écart</th>
                <th>Compté par</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredLines.map((line) => (
                <tr key={line.id} className={cn(line.difference !== 0 && "bg-red-50/30")}>
                  <td>
                    <p className="text-sm font-medium text-gray-900">{line.product_name}</p>
                    <p className="text-xs text-gray-500">{line.product_reference}</p>
                  </td>
                  <td className="text-right">
                    <span className="text-sm font-medium">{line.expected_quantity}</span>
                  </td>
                  <td className="text-right">
                    {editingLine === line.id ? (
                      <div className="flex items-center justify-end gap-2">
                        <Input
                          type="number"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="w-24 h-8 text-right"
                          autoFocus
                        />
                        <Button
                          size="sm"
                          onClick={() => handleSaveCount(line.id)}
                          loading={saving}
                        >
                          <Save className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <span className={cn(
                        "text-sm font-medium",
                        line.counted_quantity === null && "text-gray-400 italic"
                      )}>
                        {line.counted_quantity !== null ? line.counted_quantity : "Non compté"}
                      </span>
                    )}
                  </td>
                  <td className="text-right">
                    {line.counted_quantity !== null && (
                      <Badge variant={line.difference === 0 ? "success" : "danger"}>
                        {line.difference > 0 ? `+${line.difference}` : line.difference}
                      </Badge>
                    )}
                  </td>
                  <td className="text-right">
                    <span className={cn(
                      "text-sm",
                      line.difference_value !== 0 ? "text-red-600 font-medium" : "text-gray-500"
                    )}>
                      {formatCurrency(line.difference_value)}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs text-gray-500">
                      {line.counted_by_name || "-"}
                    </span>
                  </td>
                  <td>
                    {inventory.status === "IN_PROGRESS" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStartCounting(line.id)}
                      >
                        {line.counted_quantity !== null ? "Modifier" : "Compter"}
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}