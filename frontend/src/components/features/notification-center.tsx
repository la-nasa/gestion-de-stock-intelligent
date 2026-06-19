"use client"

import React, { useState, useEffect, useCallback } from "react"
import { Bell, Package, AlertTriangle, CheckCircle, Info, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { get, post } from "@/lib/api/client"

interface Notification {
  id: string
  type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
  link?: string
  priority: number
}

const notificationIcons: Record<string, React.ReactNode> = {
  INFO: <Info className="h-5 w-5 text-blue-500" />,
  WARNING: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
  ERROR: <AlertTriangle className="h-5 w-5 text-red-500" />,
  SUCCESS: <CheckCircle className="h-5 w-5 text-green-500" />,
  STOCK_LOW: <Package className="h-5 w-5 text-yellow-500" />,
  STOCK_OUT: <Package className="h-5 w-5 text-red-500" />,
  ORDER_RECEIVED: <Package className="h-5 w-5 text-green-500" />,
}

export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      const response = await get<{ data: any }>("/notifications/")
      setNotifications(response.data.notifications || [])
      setUnreadCount(response.data.unread_count || 0)
    } catch (error) {
      console.error("Erreur chargement notifications:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchNotifications()
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  }, [fetchNotifications])

  // WebSocket connection
  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) return

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/notifications/`
    const socket = new WebSocket(`${wsUrl}?token=${token}`)

    socket.onopen = () => {
      console.log("WebSocket notifications connecté")
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === "notification") {
        setNotifications((prev) => [data.notification, ...prev])
        setUnreadCount((prev) => prev + 1)
      } else if (data.type === "unread_count") {
        setUnreadCount(data.count)
      }
    }

    socket.onclose = () => {
      console.log("WebSocket notifications déconnecté")
    }

    return () => {
      socket.close()
    }
  }, [])

  const handleMarkRead = async (id: string) => {
    try {
      await post(`/notifications/${id}/read/`)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
      setUnreadCount((prev) => Math.max(0, prev - 1))
    } catch (error) {
      console.error("Erreur marquage lu:", error)
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await post("/notifications/read-all/")
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error("Erreur marquage tout lu:", error)
    }
  }

  const timeAgo = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return "À l'instant"
    if (minutes < 60) return `Il y a ${minutes}min`
    if (hours < 24) return `Il y a ${hours}h`
    return `Il y a ${days}j`
  }

  return (
    <div className="relative">
      {/* Bouton cloche */}
      <Button
        variant="ghost"
        size="icon-sm"
        className="relative"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center animate-pulse-soft">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </Button>

      {/* Panneau de notifications */}
      {isOpen && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Panneau */}
          <Card className="absolute right-0 top-12 z-50 w-96 max-h-[70vh] overflow-hidden shadow-soft-xl animate-scale-in">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <div>
                <h3 className="font-semibold text-gray-900">Notifications</h3>
                <p className="text-xs text-gray-500">
                  {unreadCount} non lue(s)
                </p>
              </div>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleMarkAllRead}
                    className="text-xs"
                  >
                    Tout lu
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => setIsOpen(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Liste */}
            <div className="overflow-y-auto max-h-[60vh]">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                  <Bell className="h-12 w-12 mb-3 opacity-30" />
                  <p className="text-sm">Aucune notification</p>
                </div>
              ) : (
                notifications.map((notif) => (
                  <button
                    key={notif.id}
                    onClick={() => handleMarkRead(notif.id)}
                    className={cn(
                      "w-full text-left p-4 border-b border-gray-50 transition-colors hover:bg-gray-50",
                      !notif.is_read && "bg-blue-50/50"
                    )}
                  >
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {notificationIcons[notif.type] || notificationIcons.INFO}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className={cn(
                            "text-sm font-medium",
                            !notif.is_read ? "text-gray-900" : "text-gray-600"
                          )}>
                            {notif.title}
                          </p>
                          {!notif.is_read && (
                            <span className="h-2 w-2 rounded-full bg-blue-500 flex-shrink-0" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500 line-clamp-2">
                          {notif.message}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {timeAgo(notif.created_at)}
                        </p>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}