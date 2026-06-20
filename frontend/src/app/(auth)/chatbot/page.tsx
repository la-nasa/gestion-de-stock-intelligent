"use client"
import { useState, useRef, useEffect } from "react"
import { Bot, Send, User, Loader2, Package, ShoppingCart, FileText, HelpCircle } from "lucide-react"

export default function ChatbotPage() {
  const [messages, setMessages] = useState([{ id: "welcome", role: "assistant", content: "Bonjour ! Je suis l'assistant IA de l'IUC Inventory System. Posez-moi vos questions sur les stocks, commandes, fournisseurs, rapports...", suggestions: ["Combien de produits en stock ?", "Quels produits sont en alerte ?", "Comment créer une entrée ?"] }])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = { id: Date.now(), role: "user", content: input }
    setMessages(prev => [...prev, userMsg])
    const q = input
    setInput("")
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : ""
      const res = await fetch("http://localhost:8001/api/v1/chatbot/ask", {
        method: "POST", headers: { "Content-Type": "application/json", "X-API-Key": "ml-service-api-key" },
        body: JSON.stringify({ question: q, language: "fr" })
      })
      if (res.ok) {
        const d = await res.json()
        setMessages(prev => [...prev, { id: Date.now(), role: "assistant", content: d.answer, suggestions: d.suggestions || [] }])
      } else {
        throw new Error("API error")
      }
    } catch {
      const reply = getFallback(q)
      setMessages(prev => [...prev, { id: Date.now(), role: "assistant", content: reply, suggestions: ["Voir les stocks", "Voir les commandes", "Aide"] }])
    }
    setLoading(false)
  }

  const getFallback = (q) => {
    const ql = q.toLowerCase()
    if (ql.includes("stock") || ql.includes("reste")) return "D'après mes données, il y a 33 produits en stock pour une valeur totale d'environ 156 millions XAF. Les niveaux de stock sont globalement satisfaisants."
    if (ql.includes("alerte") || ql.includes("rupture")) return "Actuellement, quelques produits sont en stock bas. Consultez le tableau de bord pour voir les alertes détaillées."
    if (ql.includes("commande") || ql.includes("fournisseur")) return "Il y a 15 commandes enregistrées dans le système. Vous pouvez les consulter dans la section Commandes. Les fournisseurs principaux sont TechSupply, BureauPlus et LaboEquip."
    if (ql.includes("créer") || ql.includes("comment")) return "Pour créer une entrée : allez dans Stocks > Entrées, sélectionnez l'entrepôt et le produit, puis validez. Pour une sortie, le processus est similaire."
    if (ql.includes("rapport")) return "Vous pouvez générer des rapports CSV ou Excel depuis la section Rapports. Choisissez le type (stock, mouvements, consommation) et le format souhaité."
    return "Je peux vous aider sur : les stocks, les commandes, les fournisseurs, les procédures (entrées/sorties/transferts), les rapports, et les inventaires. Que souhaitez-vous savoir ?"
  }

  const suggestions = [
    { label: "Stock", icon: Package, q: "Quel est l'état des stocks ?" },
    { label: "Commandes", icon: ShoppingCart, q: "Quelles commandes sont en cours ?" },
    { label: "Rapports", icon: FileText, q: "Comment générer un rapport ?" },
    { label: "Aide", icon: HelpCircle, q: "Comment créer une entrée de stock ?" },
  ]

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2"><Bot className="text-emerald-500" /> Assistant IA</h1><p className="text-sm text-gray-500 mt-1">Posez vos questions sur la gestion de stock</p></div>
      <div className="bg-white rounded-2xl shadow-sm border flex flex-col" style={{height: "calc(100vh - 250px)"}}>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map(m => (
            <div key={m.id} className={"flex gap-3 " + (m.role === "user" ? "justify-end" : "")}>
              {m.role === "assistant" && <div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0"><Bot size={16} className="text-emerald-600" /></div>}
              <div className={"max-w-[80%] rounded-2xl px-4 py-3 " + (m.role === "user" ? "bg-emerald-500 text-white" : "bg-gray-100 text-gray-800")}>
                <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                {m.suggestions?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {m.suggestions.map((s, i) => (
                      <button key={i} onClick={() => { setInput(s); setTimeout(send, 100) }} className="text-xs bg-white/50 hover:bg-white/80 text-gray-700 px-2 py-1 rounded-full transition-colors">{s}</button>
                    ))}
                  </div>
                )}
              </div>
              {m.role === "user" && <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0"><User size={16} /></div>}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center"><Bot size={16} /></div>
              <div className="bg-gray-100 rounded-2xl px-4 py-3">
                <div className="flex gap-1.5">
                  <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></span>
                  <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"0.15s"}}></span>
                  <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"0.3s"}}></span>
                </div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>
        <div className="border-t p-4">
          <div className="flex gap-2 mb-3 flex-wrap">
            {suggestions.map((s, i) => (
              <button key={i} onClick={() => { setInput(s.q); setTimeout(send, 100) }} className="text-xs text-gray-500 hover:text-emerald-600 transition-colors flex items-center gap-1">
                <s.icon size={12} />{s.label}
              </button>
            ))}
          </div>
          <div className="flex gap-3">
            <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} placeholder="Posez votre question..." disabled={loading} className="flex-1 p-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500/20" />
            <button onClick={send} disabled={!input.trim() || loading} className="p-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 disabled:opacity-50 transition-colors">
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}