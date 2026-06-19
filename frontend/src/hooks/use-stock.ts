"use client"

import { useState, useEffect, useCallback } from "react"
import { get, post, patch, del } from "@/lib/api/client"

interface UseStockOptions {
  warehouse?: string
  product?: string
  status?: string
}

export function useStocks(options?: UseStockOptions) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStocks = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params: Record<string, string> = {}
      if (options?.warehouse) params.warehouse = options.warehouse
      if (options?.product) params.product = options.product
      if (options?.status) params.status = options.status

      const response = await get<{ data: { results: any[] } }>("/stocks/", params)
      setData(response.data.results || [])
    } catch (err: any) {
      setError(err.message || "Erreur lors du chargement des stocks")
    } finally {
      setLoading(false)
    }
  }, [options?.warehouse, options?.product, options?.status])

  useEffect(() => {
    fetchStocks()
  }, [fetchStocks])

  return { data, loading, error, refresh: fetchStocks }
}

export function useStockMovements(stockId?: string) {
  const [movements, setMovements] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchMovements = useCallback(async () => {
    try {
      setLoading(true)
      const params = stockId ? { stock: stockId } : {}
      const response = await get<{ data: { results: any[] } }>("/movements/", params)
      setMovements(response.data.results || [])
    } catch (error) {
      console.error("Erreur chargement mouvements:", error)
    } finally {
      setLoading(false)
    }
  }, [stockId])

  useEffect(() => {
    fetchMovements()
  }, [fetchMovements])

  const createMovement = async (data: any) => {
    const response = await post<{ data: any }>("/movements/", data)
    await fetchMovements()
    return response
  }

  const validateMovement = async (id: string) => {
    await post(`/movements/${id}/validate/`)
    await fetchMovements()
  }

  return { movements, loading, refresh: fetchMovements, createMovement, validateMovement }
}
