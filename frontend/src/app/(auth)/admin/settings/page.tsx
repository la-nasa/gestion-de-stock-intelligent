"use client"
import { useState } from "react"
import { Settings, Save, Bell, Mail, Database, Shield, Check } from "lucide-react"

export default function AdminSettingsPage() {
  const [saved, setSaved] = useState(false)

  const sections = [
    { icon: Bell, title: "Notifications", fields: ["Alertes stock bas", "Notifications email", "Rappels inventaire"], color: "#0d9488" },
    { icon: Mail, title: "Email", fields: ["Serveur SMTP", "Email expéditeur", "Signature"], color: "#2563eb" },
    { icon: Database, title: "Base de données", fields: ["Sauvegarde automatique", "Rétention 30 jours", "Compression"], color: "#7c3aed" },
    { icon: Shield, title: "Sécurité", fields: ["2FA obligatoire", "Expiration mot de passe 90j", "IP whitelist"], color: "#dc2626" },
  ]

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 2000) }

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      <div><h1 className="text-2xl font-bold text-gray-800">Paramètres</h1><p className="text-sm text-gray-500">Configuration du système</p></div>
      {sections.map((s, i) => (
        <div key={i} className="bg-white rounded-2xl shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg" style={{background: s.color + "15"}}><s.icon size={20} style={{color: s.color}} /></div>
            <h3 className="font-semibold text-gray-800">{s.title}</h3>
          </div>
          <div className="space-y-3">
            {s.fields.map((f, j) => (
              <div key={j} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-sm text-gray-600">{f}</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked={j === 0} />
                  <div className="w-9 h-5 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" style={{background: j === 0 ? s.color : ""}}></div>
                </label>
              </div>
            ))}
          </div>
        </div>
      ))}
      <button onClick={handleSave} className="flex items-center gap-2 px-6 py-3 text-white rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-lg">
        {saved ? <Check size={18} /> : <Save size={18} />} {saved ? "Paramètres enregistrés !" : "Enregistrer les paramètres"}
      </button>
    </div>
  )
}