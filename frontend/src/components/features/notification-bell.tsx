"use client"
import { useState, useEffect, useCallback } from "react"
import { Bell, X, Package, AlertTriangle, CheckCircle, Info } from "lucide-react"

const API = "http://localhost:8000/api/v1"

const icons: any = { INFO: Info, WARNING: AlertTriangle, ERROR: AlertTriangle, SUCCESS: CheckCircle, STOCK_LOW: Package, STOCK_OUT: Package, ORDER_RECEIVED: Package }
const colors: any = { INFO: "text-blue-500", WARNING: "text-yellow-500", ERROR: "text-red-500", SUCCESS: "text-green-500", STOCK_LOW: "text-yellow-500", STOCK_OUT: "text-red-500", ORDER_RECEIVED: "text-green-500" }

export function NotificationBell() {
  const [notifications, setNotifications] = useState<any[]>([])
  const [unread, setUnread] = useState(0)
  const [open, setOpen] = useState(false)
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""

  const fetchNotifs = useCallback(() => {
    if (!token) return
    fetch(API + "/notifications/", { headers: { Authorization: "Bearer " + token } })
      .then(r => r.json())
      .then(d => {
        const items = d?.data?.notifications || d?.data || []
        const arr = Array.isArray(items) ? items.slice(0, 20) : []
        setNotifications(arr)
        setUnread(d?.data?.unread_count || arr.filter(n => !n.is_read).length || 0)
        if (arr.length > 0 && !arr[0].is_read) {
          try { new Audio("/notification.mp3").play().catch(() => {}) } catch {}
        }
      })
      .catch(() => {})
  }, [token])

  useEffect(() => { fetchNotifs(); const i = setInterval(fetchNotifs, 30000); return () => clearInterval(i) }, [fetchNotifs])

  const markRead = async (id: string) => {
    await fetch(API + "/notifications/" + id + "/read/", { method: "POST", headers: { Authorization: "Bearer " + token } })
    fetchNotifs()
  }
  const markAllRead = async () => {
    await fetch(API + "/notifications/read-all/", { method: "POST", headers: { Authorization: "Bearer " + token } })
    fetchNotifs()
  }

  const timeAgo = (date: string) => {
    const diff = Math.floor((Date.now() - new Date(date).getTime()) / 1000)
    if (diff < 60) return "A l'instant"
    if (diff < 3600) return "Il y a " + Math.floor(diff / 60) + "min"
    if (diff < 86400) return "Il y a " + Math.floor(diff / 3600) + "h"
    return "Il y a " + Math.floor(diff / 86400) + "j"
  }

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
        <Bell size={18} className="text-gray-500" />
        {unread > 0 && <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-1 animate-pulse">{unread > 99 ? "99+" : unread}</span>}
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-12 z-50 w-80 md:w-96 bg-white rounded-2xl shadow-2xl border overflow-hidden animate-scale-in">
            <div className="p-4 border-b flex items-center justify-between">
              <div><h3 className="font-semibold text-gray-800">Notifications</h3><p className="text-xs text-gray-400">{unread} non lue(s)</p></div>
              <div className="flex gap-2">
                {unread > 0 && <button onClick={markAllRead} className="text-xs text-emerald-600 hover:underline">Tout lu</button>}
                <button onClick={() => setOpen(false)} className="p-1 hover:bg-gray-100 rounded"><X size={16} /></button>
              </div>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-400"><Bell size={32} className="mx-auto mb-2 opacity-30" /><p className="text-sm">Aucune notification</p></div>
              ) : notifications.map(n => {
                const Icon = icons[n.type] || Info
                return (
                  <button key={n.id} onClick={() => markRead(n.id)} className={"w-full text-left p-4 border-b border-gray-50 hover:bg-gray-50 transition-colors flex gap-3 " + (!n.is_read ? "bg-blue-50/30" : "")}>
                    <Icon size={18} className={colors[n.type] || "text-gray-400"} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800">{n.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                      <p className="text-[10px] text-gray-400 mt-1">{timeAgo(n.created_at)}</p>
                    </div>
                    {!n.is_read && <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0 mt-1.5"></span>}
                  </button>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
