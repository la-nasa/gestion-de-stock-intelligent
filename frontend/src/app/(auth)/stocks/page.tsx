"use client"

import React, { useState, useEffect, useCallback } from "react"
import { DataTable } from "@/components/tables/data-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Package,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  ArrowUpDown,
} from "lucide-react"
import { type ColumnDef } from "@tanstack/react-table"
import { formatCurrency, cn } from "@/lib/utils"
import { get } from "@/lib/api/client"

interface Stock {
  id: string
  product_name: string
  product_reference: string
  warehouse_name: string
  quantity: number
  reserved_quantity: number
  available_quantity: number
  unit_price: number
  location: string
  status: string
  last_movement_date: string
}

export default function StocksPage() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [loading, setLoading] = useState(true)

  const fetchStocks = useCallback(async () => {
    try {
      setLoading(true)
      const response = await get<{ data: { results: Stock[] } }>("/stocks/")
      setStocks(response.data.results || [])
    } catch (error) {
      console.error("Erreur chargement stocks:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStocks()
  }, [fetchStocks])

  const totalValue = stocks.reduce(
    (sum, s) => sum + s.quantity * s.unit_price,
    0
  )
  const lowStockCount = stocks.filter((s) => s.status === "low").length
  const outOfStockCount = stocks.filter((s) => s.status === "out_of_stock").length

  const columns: ColumnDef<Stock>[] = [
    {
      accessorKey: "product_name",
      header: "Produit",
      cell: ({ row }) => (
        <div>
          <p className="text-sm font-medium text-gray-900">
            {row.original.product_name}
          </p>
          <p className="text-xs text-gray-500">{row.original.product_reference}</p>
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
      accessorKey: "quantity",
      header: "Quantité",
      cell: ({ row }) => {
        const status = row.original.status
        return (
          <div>
            <span
              className={cn(
                "text-sm font-medium",
                status === "out_of_stock" && "text-red-600",
                status === "low" && "text-yellow-600",
                status === "normal" && "text-green-600"
              )}
            >
              {row.original.quantity}
            </span>
            {row.original.reserved_quantity > 0 && (
              <span className="text-xs text-gray-400 ml-1">
                ({row.original.reserved_quantity} rés.)
              </span>
            )}
          </div>
        )
      },
    },
    {
      accessorKey: "available_quantity",
      header: "Disponible",
      cell: ({ row }) => (
        <span className="text-sm font-medium text-gray-900">
          {row.original.available_quantity}
        </span>
      ),
    },
    {
      accessorKey: "unit_price",
      header: "Prix unitaire",
      cell: ({ row }) => formatCurrency(row.original.unit_price),
    },
    {
      id: "total_value",
      header: "Valeur totale",
      cell: ({ row }) =>
        formatCurrency(row.original.quantity * row.original.unit_price),
    },
    {
      accessorKey: "location",
      header: "Emplacement",
      cell: ({ row }) => (
        <span className="text-xs text-gray-500">
          {row.original.location || "-"}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stocks</h1>
          <p className="text-sm text-gray-500 mt-1">
            Vue d'ensemble des stocks par entrepôt
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <ArrowUpDown className="h-4 w-4 mr-2" />
            Transfert
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-50">
                <Package className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stocks.length}</p>
                <p className="text-xs text-gray-500">Articles en stock</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-50">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{formatCurrency(totalValue)}</p>
                <p className="text-xs text-gray-500">Valeur totale</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-yellow-50">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{lowStockCount}</p>
                <p className="text-xs text-gray-500">Stocks bas</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-50">
                <TrendingDown className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{outOfStockCount}</p>
                <p className="text-xs text-gray-500">Ruptures</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tableau */}
      <DataTable
        columns={columns}
        data={stocks}
        searchKey="product_name"
        searchPlaceholder="Rechercher un produit..."
        isLoading={loading}
      />
    </div>
  )
}
