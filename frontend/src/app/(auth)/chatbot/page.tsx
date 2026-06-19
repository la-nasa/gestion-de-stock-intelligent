"use client"

import React, { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { toast } from "react-hot-toast"
import {
  Bot,
  Send,
  User,
  Sparkles,
  Package,
  ShoppingCart,
  FileText,
  HelpCircle,
  X,
  Loader2,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
  confidence?: number
  suggestions?: string[]
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Bonjour ! 👋 Je suis l'assistant IA de l'IUC Inventory System. Je peux vous aider avec :\n\n" +
        "📦 **Stocks** - Vérifier les quantités, alertes\n" +
        "📋 **Commandes** - Suivi, création\n" +
        "📊 **Rapports** - Consommation, analyses\n" +
        "🔍 **Procédures** - Comment faire\n\n" +
        "Posez-moi votre question !",
      timestamp: new Date().toISOString(),
      suggestions: [
        "Combien reste-t-il d'ordinateurs ?",
        "Quels produits sont en rupture ?",
        "Quel département consomme le plus ?",
      ],
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_ML_SERVICE_URL || "http://localhost:8001"}/api/v1/chatbot/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": "ml-service-api-key-change-in-production",
          },
          body: JSON.stringify({
            question: userMessage.content,
            user_id: "web_user",
            language: "fr",
          }),
        }
      )

      if (!response.ok) throw new Error("Erreur chatbot")

      const data = await response.json()

      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: "assistant",
        content: data.answer,
        timestamp: data.timestamp,
        confidence: data.confidence,
        suggestions: data.suggestions,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast.error("Erreur de communication avec l'assistant")
      
      // Fallback réponse
      setMessages((prev) => [
        ...prev,
        {
          id: `error_${Date.now()}`,
          role: "assistant",
          content:
            "Désolé, je rencontre des difficultés techniques. Veuillez réessayer.",
          timestamp: new Date().toISOString(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion)
    setTimeout(() => handleSend(), 100)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bot className="h-6 w-6 text-primary-500" />
          Assistant IA
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Posez vos questions sur la gestion de stock
        </p>
      </div>

      {/* Chat */}
      <Card className="h-[calc(100vh-250px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-3 animate-slide-up",
                message.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {message.role === "assistant" && (
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="h-4 w-4 text-primary-600" />
                </div>
              )}

              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3",
                  message.role === "user"
                    ? "bg-primary-500 text-white rounded-br-md"
                    : "bg-gray-100 text-gray-900 rounded-bl-md"
                )}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                {message.confidence && (
                  <div className="flex items-center gap-2 mt-2">
                    <div className="text-xs opacity-70">
                      Confiance: {Math.round(message.confidence * 100)}%
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {message.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-xs bg-white/50 hover:bg-white/80 text-gray-700 px-2.5 py-1 rounded-full transition-colors border border-gray-200"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {message.role === "user" && (
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 animate-slide-up">
              <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-600" />
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1">
                  <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Posez votre question..."
              disabled={loading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              size="icon"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Quick suggestions */}
          <div className="flex gap-2 mt-3 flex-wrap">
            <button
              onClick={() => handleSuggestionClick("Combien reste-t-il d'ordinateurs ?")}
              className="text-xs text-gray-500 hover:text-primary-600 transition-colors"
            >
              <Package className="h-3 w-3 inline mr-1" />
              Stock
            </button>
            <button
              onClick={() => handleSuggestionClick("Quelles commandes sont en cours ?")}
              className="text-xs text-gray-500 hover:text-primary-600 transition-colors"
            >
              <ShoppingCart className="h-3 w-3 inline mr-1" />
              Commandes
            </button>
            <button
              onClick={() => handleSuggestionClick("Comment générer un rapport ?")}
              className="text-xs text-gray-500 hover:text-primary-600 transition-colors"
            >
              <FileText className="h-3 w-3 inline mr-1" />
              Rapports
            </button>
            <button
              onClick={() => handleSuggestionClick("Comment créer une entrée de stock ?")}
              className="text-xs text-gray-500 hover:text-primary-600 transition-colors"
            >
              <HelpCircle className="h-3 w-3 inline mr-1" />
              Aide
            </button>
          </div>
        </div>
      </Card>
    </div>
  )
}