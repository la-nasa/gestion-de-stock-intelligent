"use client"

import React, { createContext, useContext, useEffect, useCallback } from "react"
import { useWebSocket } from "@/hooks/use-websocket"
import { toast } from "react-hot-toast"

interface WebSocketContextType {
  status: string
  send: (data: any) => void
  isConnected: boolean
}

const WebSocketContext = createContext<WebSocketContextType>({
  status: "disconnected",
  send: () => {},
  isConnected: false,
})

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"

  const { status, send, isConnected } = useWebSocket({
    url: `${wsUrl}/ws/notifications/`,
    autoReconnect: true,
    reconnectInterval: 5000,
    onMessage: (data) => {
      // Gérer les différents types de messages
      switch (data.type) {
        case "notification":
          toast(data.notification.title, {
            description: data.notification.message,
            icon: getNotificationIcon(data.notification.type),
          })
          break
        case "low_stock_alert":
          toast.error(
            `⚠️ Stock bas : ${data.alert?.product_name || "Produit"}`
          )
          break
        case "stock_update":
          // Rafraîchir les données si nécessaire
          break
        case "broadcast":
          if (data.level === "warning") {
            toast(data.message, { icon: "⚠️" })
          } else if (data.level === "error") {
            toast.error(data.message)
          } else {
            toast(data.message)
          }
          break
      }
    },
  })

  return (
    <WebSocketContext.Provider value={{ status, send, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWS = () => useContext(WebSocketContext)

function getNotificationIcon(type: string): string {
  switch (type) {
    case "SUCCESS":
      return "✅"
    case "WARNING":
    case "STOCK_LOW":
      return "⚠️"
    case "ERROR":
    case "STOCK_OUT":
      return "🚨"
    case "ORDER_RECEIVED":
      return "📦"
    default:
      return "🔔"
  }
}