"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Package,
  Warehouse,
  ShoppingCart,
  ArrowRightLeft,
  ClipboardList,
  BarChart3,
  Settings,
  Users,
  Bell,
  FileText,
  QrCode,
  Wrench,
  ChevronDown,
  ChevronRight,
  type LucideIcon,
} from "lucide-react"

interface NavItem {
  title: string
  href?: string
  icon: LucideIcon
  children?: Omit<NavItem, "icon" | "children">[]
  badge?: string
}

const navigation: NavItem[] = [
  {
    title: "Tableau de bord",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Produits",
    icon: Package,
    children: [
      { title: "Tous les produits", href: "/products" },
      { title: "Catégories", href: "/categories" },
      { title: "Fournisseurs", href: "/suppliers" },
    ],
  },
  {
    title: "Stocks",
    icon: Warehouse,
    children: [
      { title: "Vue d'ensemble", href: "/stocks" },
      { title: "Entrées", href: "/stocks/entries" },
      { title: "Sorties", href: "/stocks/outputs" },
      { title: "Transferts", href: "/stocks/transfers" },
    ],
  },
  {
    title: "Commandes",
    href: "/orders",
    icon: ShoppingCart,
  },
  {
    title: "Inventaires",
    href: "/inventories",
    icon: ClipboardList,
  },
  {
    title: "Rapports",
    icon: FileText,
    children: [
      { title: "Générer un rapport", href: "/reports" },
      { title: "Rapports planifiés", href: "/reports/scheduled" },
    ],
  },
  {
    title: "Analytiques",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    title: "QR Codes",
    href: "/qr-codes",
    icon: QrCode,
  },
  {
    title: "Maintenance",
    href: "/maintenance",
    icon: Wrench,
  },
  {
    title: "Administration",
    icon: Settings,
    children: [
      { title: "Utilisateurs", href: "/admin/users" },
      { title: "Rôles", href: "/admin/roles" },
      { title: "Audit", href: "/admin/audit" },
      { title: "Paramètres", href: "/admin/settings" },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [expandedItems, setExpandedItems] = React.useState<string[]>([])

  const toggleExpand = (title: string) => {
    setExpandedItems((prev) =>
      prev.includes(title)
        ? prev.filter((t) => t !== title)
        : [...prev, title]
    )
  }

  const isActive = (href: string) => pathname === href || pathname?.startsWith(href + "/")

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-gray-200">
        <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center">
          <span className="text-white font-bold text-sm">IUC</span>
        </div>
        <div>
          <h1 className="text-sm font-bold text-gray-900">IUC Inventory</h1>
          <p className="text-xs text-gray-500">Gestion de stock</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon
          const isExpanded = expandedItems.includes(item.title)

          if (item.children) {
            return (
              <div key={item.title}>
                <button
                  onClick={() => toggleExpand(item.title)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                    "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  )}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  <span className="flex-1 text-left">{item.title}</span>
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </button>

                {isExpanded && (
                  <div className="ml-4 mt-1 space-y-1">
                    {item.children.map((child) => (
                      <Link
                        key={child.href}
                        href={child.href!}
                        className={cn(
                          "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                          isActive(child.href!)
                            ? "bg-primary-50 text-primary-700 font-medium"
                            : "text-gray-500 hover:bg-gray-50 hover:text-gray-700"
                        )}
                      >
                        <span className="w-1 h-1 rounded-full bg-current opacity-50" />
                        {child.title}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )
          }

          return (
            <Link
              key={item.href}
              href={item.href!}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive(item.href!)
                  ? "bg-primary-50 text-primary-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              <span>{item.title}</span>
              {item.badge && (
                <span className="ml-auto bg-primary-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
            <Users className="h-4 w-4 text-primary-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              Admin IUC
            </p>
            <p className="text-xs text-gray-500 truncate">admin@iuc.cm</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
