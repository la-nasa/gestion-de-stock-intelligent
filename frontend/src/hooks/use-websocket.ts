"use client"

import { useEffect, useRef, useCallback, useState } from "react"

type MessageHandler = (data: any) => void
type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error"

interface UseWebSocketOptions {
  url: string
  onMessage?: MessageHandler
  onOpen?: () => void
  onClose?: (code: number) => void
  onError?: (error: Event) => void
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  autoReconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 10,
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const [status, setStatus] = useState<ConnectionStatus>("disconnected")
  const [lastMessage, setLastMessage] = useState<any>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    // Ajouter le token JWT
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
    const fullUrl = token ? `${url}?token=${token}` : url

    try {
      setStatus("connecting")
      const ws = new WebSocket(fullUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus("connected")
        reconnectAttemptsRef.current = 0
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          onMessage?.(data)
        } catch {
          onMessage?.(event.data)
        }
      }

      ws.onclose = (event) => {
        setStatus("disconnected")
        onClose?.(event.code)

        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        setStatus("error")
        onError?.(error)
      }
    } catch (error) {
      setStatus("error")
      console.error("WebSocket connection error:", error)
    }
  }, [url, onMessage, onOpen, onClose, onError, autoReconnect, reconnectInterval, maxReconnectAttempts])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    wsRef.current?.close()
    wsRef.current = null
    setStatus("disconnected")
  }, [])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = typeof data === "string" ? data : JSON.stringify(data)
      wsRef.current.send(message)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    status,
    lastMessage,
    send,
    connect,
    disconnect,
    isConnected: status === "connected",
  }
}