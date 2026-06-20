"use client"
import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard, Package, Warehouse, ShoppingCart,
  ClipboardList, BarChart3, Settings, FileText, QrCode,
  Wrench, ChevronDown, ChevronRight, GraduationCap, Bot,
  FileSearch, X, Shield, Key
} from "lucide-react"

interface NavItem {
  title: string
  href?: string
  icon: any
  children?: { title: string; href: string }[]
}

const navigation: NavItem[] = [
  { title: "Tableau de bord", href: "/dashboard", icon: LayoutDashboard },
  { title: "Produits", icon: Package, children: [
    { title: "Tous les produits", href: "/products" },
    { title: "Catégories", href: "/categories" },
    { title: "Fournisseurs", href: "/suppliers" },
  ]},
  { title: "Stocks", icon: Warehouse, children: [
    { title: "Vue d'ensemble", href: "/stocks" },
    { title: "Entrées", href: "/stocks/entries" },
    { title: "Sorties", href: "/stocks/outputs" },
    { title: "Transferts", href: "/stocks/transfers" },
  ]},
  { title: "Commandes", href: "/orders", icon: ShoppingCart },
  { title: "Inventaires", href: "/inventories", icon: ClipboardList },
  { title: "Rapports", icon: FileText, children: [
    { title: "Générer un rapport", href: "/reports" },
    { title: "Rapports planifiés", href: "/reports/scheduled" },
  ]},
  { title: "Analytiques", href: "/analytics", icon: BarChart3 },
  { title: "QR Codes", href: "/qr-codes", icon: QrCode },
  { title: "Chatbot IA", href: "/chatbot", icon: Bot },
  { title: "Maintenance", href: "/maintenance", icon: Wrench },
  { title: "Administration", icon: Settings, children: [
    { title: "Utilisateurs", href: "/admin/users" },
    { title: "Rôles", href: "/admin/roles" },
    { title: "Permissions", href: "/admin/permissions" },
    { title: "Entrepôts", href: "/admin/warehouses" },
    { title: "Audit", href: "/admin/audit" },
    { title: "Paramètres", href: "/admin/settings" },
  ]},
]

export function Sidebar({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname()
  const [expanded, setExpanded] = React.useState<string[]>([])
  const toggle = (t: string) => setExpanded(p => p.includes(t) ? p.filter(x => x !== t) : [...p, t])
  const isActive = (href: string) => pathname === href || pathname?.startsWith(href + "/")

  return (
    <aside className="h-screen w-64 flex flex-col shadow-xl" style={{background: "linear-gradient(180deg, #1e3a5f 0%, #1a3354 30%, #15294a 100%)"}}>
      <div className="h-16 flex items-center gap-3 px-5 border-b border-white/10">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg">
          <GraduationCap size={18} className="text-white" />
        </div>
        <div className="flex-1">
          <h1 className="text-sm font-bold text-white tracking-wide">IUC Inventory</h1>
          <p className="text-[10px] text-emerald-300/80">Gestion de stock</p>
        </div>
        <button onClick={onClose} className="lg:hidden text-white/70 hover:text-white">
          <X size={18} />
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        {navigation.map((item) => {
          const Icon = item.icon
          const isExpanded = expanded.includes(item.title)
          if (item.children) {
            return (
              <div key={item.title}>
                <button onClick={() => toggle(item.title)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-all">
                  <Icon size={18} />
                  <span className="flex-1 text-left">{item.title}</span>
                  {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </button>
                {isExpanded && (
                  <div className="ml-4 mt-0.5 space-y-0.5">
                    {item.children.map((child) => (
                      <Link key={child.href} href={child.href}
                        className={"flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all " + (
                          isActive(child.href) ? "bg-gradient-to-r from-emerald-500/20 to-teal-500/10 text-emerald-300 font-medium border-l-2 border-emerald-400" : "text-white/50 hover:bg-white/5 hover:text-white/80"
                        )}>
                        {child.title}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )
          }
          return (
            <Link key={item.href} href={item.href!}
              className={"flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all " + (
                isActive(item.href!) ? "bg-gradient-to-r from-emerald-500/20 to-teal-500/10 text-white font-medium shadow-sm" : "text-white/70 hover:bg-white/10 hover:text-white"
              )}>
              <Icon size={18} />
              <span>{item.title}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xs font-bold">A</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">Admin IUC</p>
            <p className="text-xs text-emerald-300/60 truncate">admin@iuc.cm</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
