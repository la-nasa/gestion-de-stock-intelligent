"use client"

import React, { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { DataTable } from "@/components/tables/data-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Plus,
  Search,
  Download,
  Filter,
  Package,
  Pencil,
  Trash2,
  QrCode,
  MoreHorizontal,
} from "lucide-react"
import { type ColumnDef } from "@tanstack/react-table"
import { formatCurrency, formatDate, cn } from "@/lib/utils"
import { get, del } from "@/lib/api/client"

interface Product {
  id: string
  name: string
  reference: string
  sku: string
  category_name: string
  supplier_name: string
  unit_price: number
  currency: string
  total_stock: number
  min_stock: number
  stock_status: string
  status: string
  image: string | null
  updated_at: string
}

export default function ProductsPage() {
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true)
      const response = await get<{ data: { results: Product[] } }>("/products/")
      setProducts(response.data.results || [])
    } catch (error) {
      console.error("Erreur chargement produits:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  const handleDelete = async (id: string) => {
    if (confirm("Supprimer ce produit ?")) {
      try {
        await del(`/products/${id}/`)
        fetchProducts()
      } catch (error) {
        console.error("Erreur suppression:", error)
      }
    }
  }

  const columns: ColumnDef<Product>[] = [
    {
      accessorKey: "name",
      header: "Produit",
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center overflow-hidden">
            {row.original.image ? (
              <img src={row.original.image} alt="" className="h-full w-full object-cover" />
            ) : (
              <Package className="h-5 w-5 text-gray-400" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{row.original.name}</p>
            <p className="text-xs text-gray-500">{row.original.reference}</p>
          </div>
        </div>
      ),
    },
    {
      accessorKey: "category_name",
      header: "Catégorie",
      cell: ({ row }) => (
        <Badge variant="secondary">{row.original.category_name}</Badge>
      ),
    },
    {
      accessorKey: "total_stock",
      header: "Stock",
      cell: ({ row }) => {
        const status = row.original.stock_status
        return (
          <div>
            <span className={cn(
              "text-sm font-medium",
              status === "out_of_stock" && "text-red-600",
              status === "low_stock" && "text-yellow-600",
              status === "normal" && "text-green-600",
            )}>
              {row.original.total_stock}
            </span>
            {status === "low_stock" && (
              <Badge variant="warning" className="ml-2 text-xs">Bas</Badge>
            )}
            {status === "out_of_stock" && (
              <Badge variant="danger" className="ml-2 text-xs">Rupture</Badge>
            )}
          </div>
        )
      },
    },
    {
      accessorKey: "unit_price",
      header: "Prix unitaire",
      cell: ({ row }) => formatCurrency(row.original.unit_price, row.original.currency),
    },
    {
      accessorKey: "supplier_name",
      header: "Fournisseur",
      cell: ({ row }) => (
        <span className="text-sm text-gray-600">
          {row.original.supplier_name || "-"}
        </span>
      ),
    },
    {
      accessorKey: "updated_at",
      header: "Mis à jour",
      cell: ({ row }) => (
        <span className="text-xs text-gray-500">
          {formatDate(row.original.updated_at)}
        </span>
      ),
    },
    {
      id: "actions",
      cell: ({ row }) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/products/${row.original.id}`)
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/qr-codes/${row.original.id}`)
            }}
          >
            <QrCode className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={(e) => {
              e.stopPropagation()
              handleDelete(row.original.id)
            }}
          >
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Produits</h1>
          <p className="text-sm text-gray-500 mt-1">
            {products.length} produit(s) au total
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exporter
          </Button>
          <Button onClick={() => router.push("/products/new")}>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau produit
          </Button>
        </div>
      </div>

      {/* Filtres rapides */}
      <div className="flex items-center gap-3">
        <div className="flex-1 max-w-sm">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Rechercher un produit..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          Filtres
        </Button>
      </div>

      {/* Tableau */}
      <DataTable
        columns={columns}
        data={products}
        searchKey="name"
        searchPlaceholder="Rechercher par nom..."
        isLoading={loading}
        onRowClick={(row) => router.push(`/products/${row.id}`)}
      />
    </div>
  )
}
