"use client"

import { useState, useEffect } from "react"
import { get } from "@/lib/api/client"

interface DashboardData {
  kpis: {
    totalProducts: number
    stockValue: number
    pendingOrders: number
    lowStockItems: number
    activeTransfers: number
    totalSuppliers: number
  }
  monthlyConsumption: Array<{
    month: string
    [key: string]: number | string
  }>
  stockByCategory: Array<{
    name: string
    value: number
    color: string
  }>
  topProducts: Array<{
    name: string
    quantity: number
    value: number
  }>
  recentActivities: Array<{
    id: string
    type: "entry" | "output" | "transfer" | "inventory" | "maintenance"
    product: string
    quantity?: number
    user: string
    warehouse?: string
    time: string
  }>
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboard = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await get<{ data: DashboardData }>("/dashboard/")
      setData(response.data)
    } catch (err: any) {
      setError(err.message || "Erreur lors du chargement du dashboard")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
  }, [])

  return {
    data,
    loading,
    error,
    refresh: fetchDashboard,
  }
}
