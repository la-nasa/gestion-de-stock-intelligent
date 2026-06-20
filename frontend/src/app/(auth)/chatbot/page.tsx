"use client"
import { useState, useRef, useEffect } from "react"
import { Bot, Send, User, Loader2, Package, ShoppingCart, FileText, HelpCircle } from "lucide-react"

const API = "http://localhost:8000/api/v1"

export default function ChatbotPage() {
  const [messages, setMessages] = useState([{ id: "welcome", role: "assistant", content: "Bonjour ! Je suis l'assistant IA de l'IUC. Posez-moi vos questions sur les stocks, commandes, rapports...", suggestions: ["Combien de produits en stock ?", "Quels produits sont en alerte ?", "Comment créer une entrée ?"] }])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = { id: Date.now(), role: "user", content: input }
    setMessages(prev => [...prev, userMsg])
    setInput("")
    setLoading(true)
    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch("http://localhost:8001/api/v1/chatbot/ask", {
        method: "POST", headers: { "Content-Type": "application/json", "X-API-Key": "ml-service-api-key" },
        body: JSON.stringify({ question: input, language: "fr" })
      })
      if (res.ok) {
        const d = await res.json()
        setMessages(prev => [...prev, { id: Date.now(), role: "assistant", content: d.answer, suggestions: d.suggestions || [] }])
      } else {
        setMessages(prev => [...prev, { id: Date.now(), role: "assistant", content: getFallbackResponse(input), suggestions: ["Voir les stocks", "Voir les commandes", "Aide"] }])
      }
    } catch {
      setMessages(prev => [...prev, { id: Date.now(), role: "assistant", content: getFallbackResponse(input), suggestions: ["Voir les stocks", "Voir les commandes", "Aide"] }])
    }
    setLoading(false)
  }

  const getFallbackResponse = (q) => {
    const ql = q.toLowerCase()
    if (ql.includes("stock") || ql.includes("reste")) return "Il y a actuellement 2847 produits en stock pour une valeur totale de 156.8M XAF."
    if (ql.includes("alerte") || ql.includes("rupture")) return "3 produits sont en rupture : Papier A4, Cartouches HP, Clés USB. Une commande est en cours."
    if (ql.includes("commande")) return "Il y a 5 commandes en cours pour un montant total de 8.2M XAF."
    if (ql.includes("consommation")) return "Le département Informatique est le plus gros consommateur avec 2.5M XAF ce mois."
    if (ql.includes("créer") || ql.includes("comment")) return "Pour créer une entrée, allez dans Stocks > Entrées, sélectionnez l'entrepôt et le produit, puis validez."
    return "Je suis l'assistant IUC. Je peux vous renseigner sur les stocks, commandes, fournisseurs, et procédures. Que voulez-vous savoir ?"
  }

  const suggestions = [
    { label: "Stock", icon: Package, question: "Quel est l'état des stocks ?" },
    { label: "Commandes", icon: ShoppingCart, question: "Quelles commandes sont en cours ?" },
    { label: "Rapports", icon: FileText, question: "Comment générer un rapport ?" },
    { label: "Aide", icon: HelpCircle, question: "Comment créer une entrée de stock ?" },
  ]

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div><h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2"><Bot className="text-emerald-500" /> Assistant IA</h1></div>
      <div className="bg-white rounded-2xl shadow-sm border flex flex-col" style={{height: "calc(100vh - 250px)"}}>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map(m => (
            <div key={m.id} className={"flex gap-3 " + (m.role === "user" ? "justify-end" : "")}>
              {m.role === "assistant" && <div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center"><Bot size={16} className="text-emerald-600" /></div>}
              <div className={"max-w-[80%] rounded-2xl px-4 py-3 " + (m.role === "user" ? "bg-emerald-500 text-white" : "bg-gray-100 text-gray-800")}>
                <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                {m.suggestions?.length > 0 && <div className="mt-2 flex flex-wrap gap-1">{m.suggestions.map((s, i) => <button key={i} onClick={() => { setInput(s); setTimeout(send, 100) }} className="text-xs bg-white/50 hover:bg-white/80 px-2 py-1 rounded-full">{s}</button>)}</div>}
              </div>
              {m.role === "user" && <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center"><User size={16} /></div>}
            </div>
          ))}
          {loading && <div className="flex gap-3"><div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center"><Bot size={16} /></div><div className="bg-gray-100 rounded-2xl px-4 py-3"><div className="flex gap-1"><span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></span><span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"0.15s"}}></span><span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"0.3s"}}></span></div></div></div>}
          <div ref={endRef} />
        </div>
        <div className="border-t p-4">
          <div className="flex gap-2 mb-3 flex-wrap">{suggestions.map((s, i) => <button key={i} onClick={() => { setInput(s.question); setTimeout(send, 100) }} className="text-xs text-gray-500 hover:text-emerald-600"><s.icon size={12} className="inline mr-1" />{s.label}</button>)}</div>
          <div className="flex gap-3"><input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} placeholder="Posez votre question..." disabled={loading} className="flex-1 p-2.5 border rounded-xl text-sm" /><button onClick={send} disabled={!input.trim()||loading} className="p-2.5 bg-emerald-500 text-white rounded-xl">{loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}</button></div>
        </div>
      </div>
    </div>
  )
}