"use client"

import React, { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { DataTable } from "@/components/tables/data-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Plus,
  ClipboardList,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
} from "lucide-react"
import { type ColumnDef } from "@tanstack/react-table"
import { formatDate, formatCurrency, cn } from "@/lib/utils"
import { get } from "@/lib/api/client"
import { KPICard } from "@/components/dashboard/kpi-card"

interface Inventory {
  id: string
  reference: string
  type: string
  status: string
  warehouse_name: string
  start_date: string
  end_date: string | null
  expected_items: number
  counted_items: number
  differences: number
  total_value_expected: number
  total_value_counted: number
  value_difference: number
  supervisor_name: string
}

const typeLabels: Record<string, string> = {
  FULL: "Complet",
  PARTIAL: "Partiel",
  CYCLE: "Tournant",
  SPOT: "Ponctuel",
}

const statusConfig: Record<string, { label: string; variant: "success" | "warning" | "info" | "danger" | "secondary" }> = {
  PLANNED: { label: "Planifié", variant: "info" },
  IN_PROGRESS: { label: "En cours", variant: "warning" },
  COMPLETED: { label: "Terminé", variant: "success" },
  VALIDATED: { label: "Validé", variant: "success" },
  CANCELLED: { label: "Annulé", variant: "danger" },
}

export default function InventoriesPage() {
  const router = useRouter()
  const [inventories, setInventories] = useState<Inventory[]>([])
  const [loading, setLoading] = useState(true)

  const fetchInventories = useCallback(async () => {
    try {
      setLoading(true)
      const response = await get<{ data: { results: Inventory[] } }>("/inventories/")
      setInventories(response.data.results || [])
    } catch (error) {
      console.error("Erreur chargement inventaires:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchInventories()
  }, [fetchInventories])

  // Statistiques
  const totalInventories = inventories.length
  const inProgress = inventories.filter((i) => i.status === "IN_PROGRESS").length
  const completed = inventories.filter((i) => i.status === "COMPLETED" || i.status === "VALIDATED").length
  const totalDifferences = inventories.reduce((sum, i) => sum + Math.abs(i.value_difference), 0)

  const columns: ColumnDef<Inventory>[] = [
    {
      accessorKey: "reference",
      header: "Référence",
      cell: ({ row }) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.original.reference}</p>
          <p className="text-xs text-gray-500">{typeLabels[row.original.type]}</p>
        </div>
      ),
    },
    {
      accessorKey: "warehouse_name",
      header: "Entrepôt",
      cell: ({ row }) => (
        <Badge variant="secondary">{row.original.warehouse_name}</Badge>
      ),
    },
    {
      accessorKey: "status",
      header: "Statut",
      cell: ({ row }) => {
        const config = statusConfig[row.original.status]
        return <Badge variant={config.variant}>{config.label}</Badge>
      },
    },
    {
      accessorKey: "start_date",
      header: "Date début",
      cell: ({ row }) => formatDate(row.original.start_date),
    },
    {
      id: "progress",
      header: "Progression",
      cell: ({ row }) => {
        const pct = row.original.expected_items > 0
          ? Math.round((row.original.counted_items / row.original.expected_items) * 100)
          : 0
        return (
          <div className="flex items-center gap-2">
            <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  pct >= 100 ? "bg-green-500" : "bg-blue-500"
                )}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">{pct}%</span>
          </div>
        )
      },
    },
    {
      id: "differences",
      header: "Écarts",
      cell: ({ row }) => {
        const diff = row.original.differences
        return (
          <span className={cn(
            "text-sm font-medium",
            diff === 0 ? "text-green-600" : "text-red-600"
          )}>
            {diff > 0 ? `+${diff}` : diff}
          </span>
        )
      },
    },
    {
      accessorKey: "value_difference",
      header: "Écart valeur",
      cell: ({ row }) => {
        const diff = row.original.value_difference
        return (
          <span className={cn(
            "text-sm",
            diff === 0 ? "text-gray-400" : diff > 0 ? "text-red-600" : "text-green-600"
          )}>
            {formatCurrency(diff)}
          </span>
        )
      },
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventaires</h1>
          <p className="text-sm text-gray-500 mt-1">
            Gestion des sessions d'inventaire
          </p>
        </div>
        <Button onClick={() => router.push("/inventories/new")}>
          <Plus className="h-4 w-4 mr-2" />
          Nouvel inventaire
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard
          title="Total inventaires"
          value={totalInventories}
          icon={ClipboardList}
          iconColor="text-blue-600"
          iconBg="bg-blue-50"
        />
        <KPICard
          title="En cours"
          value={inProgress}
          icon={Play}
          iconColor="text-yellow-600"
          iconBg="bg-yellow-50"
        />
        <KPICard
          title="Terminés"
          value={completed}
          icon={CheckCircle}
          iconColor="text-green-600"
          iconBg="bg-green-50"
        />
        <KPICard
          title="Écarts totaux"
          value={formatCurrency(totalDifferences)}
          icon={AlertTriangle}
          iconColor="text-red-600"
          iconBg="bg-red-50"
        />
      </div>

      {/* Tableau */}
      <DataTable
        columns={columns}
        data={inventories}
        searchKey="reference"
        searchPlaceholder="Rechercher un inventaire..."
        isLoading={loading}
        onRowClick={(row) => router.push(`/inventories/${row.id}`)}
      />
    </div>
  )
}