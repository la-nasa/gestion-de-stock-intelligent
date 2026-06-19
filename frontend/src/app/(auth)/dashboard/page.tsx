"use client"

import React, { useState, useEffect } from "react"
import {
  Package,
  DollarSign,
  ShoppingCart,
  AlertTriangle,
  ArrowUpDown,
  Warehouse,
  Users,
  TrendingUp,
} from "lucide-react"
import { KPICard } from "@/components/dashboard/kpi-card"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { BaseChart } from "@/components/charts/base-chart"
import { BarChart } from "@/components/charts/bar-chart"
import { LineChart } from "@/components/charts/line-chart"
import { PieChart } from "@/components/charts/pie-chart"
import { Button } from "@/components/ui/button"
import { formatCurrency, formatNumber } from "@/lib/utils"

// Données mockées pour le dashboard
const mockKPIs = {
  totalProducts: { value: 2847, change: "+12.5%", trend: "up" as const },
  stockValue: { value: "156.8M XAF", change: "+8.2%", trend: "up" as const },
  pendingOrders: { value: 24, change: "-3.1%", trend: "down" as const },
  lowStockItems: { value: 18, change: "+5.5%", trend: "up" as const },
  activeTransfers: { value: 7, change: "+2", trend: "up" as const },
  totalSuppliers: { value: 86, change: "+4", trend: "up" as const },
}

const monthlyConsumption = [
  { month: "Jan", Informatique: 4500000, Bureautique: 2300000, Laboratoire: 1800000 },
  { month: "Fév", Informatique: 5200000, Bureautique: 2100000, Laboratoire: 1950000 },
  { month: "Mar", Informatique: 4800000, Bureautique: 2500000, Laboratoire: 2100000 },
  { month: "Avr", Informatique: 6100000, Bureautique: 2800000, Laboratoire: 2200000 },
  { month: "Mai", Informatique: 5500000, Bureautique: 2600000, Laboratoire: 2400000 },
  { month: "Juin", Informatique: 6300000, Bureautique: 2900000, Laboratoire: 2600000 },
  { month: "Juil", Informatique: 5800000, Bureautique: 2700000, Laboratoire: 2500000 },
  { month: "Août", Informatique: 4900000, Bureautique: 2400000, Laboratoire: 2300000 },
  { month: "Sep", Informatique: 6700000, Bureautique: 3100000, Laboratoire: 2800000 },
  { month: "Oct", Informatique: 7200000, Bureautique: 3200000, Laboratoire: 2900000 },
  { month: "Nov", Informatique: 6900000, Bureautique: 3000000, Laboratoire: 3100000 },
  { month: "Déc", Informatique: 7500000, Bureautique: 3400000, Laboratoire: 3300000 },
]

const stockByCategory = [
  { name: "Informatique", value: 45000000, color: "#1e40af" },
  { name: "Bureautique", value: 28000000, color: "#166534" },
  { name: "Laboratoire", value: 22000000, color: "#ca8a04" },
  { name: "Mobilier", value: 18000000, color: "#7c3aed" },
  { name: "Consommables", value: 12000000, color: "#0891b2" },
]

const topProducts = [
  { name: "Ordinateur Dell OptiPlex", quantity: 450, value: 22500000 },
  { name: "Projecteur Epson EB-X51", quantity: 120, value: 36000000 },
  { name: "Papier A4 (ramette)", quantity: 5000, value: 12500000 },
  { name: "Imprimante HP LaserJet", quantity: 85, value: 21250000 },
  { name: "Microscope Olympus", quantity: 35, value: 17500000 },
]

const mockActivities = [
  { id: "1", type: "entry" as const, product: "Ordinateurs Dell OptiPlex", quantity: 50, user: "Jean Kouam", warehouse: "Entrepôt Principal", time: "Il y a 2h" },
  { id: "2", type: "output" as const, product: "Papier A4", quantity: 200, user: "Marie Ngo", warehouse: "Entrepôt Campus B", time: "Il y a 3h" },
  { id: "3", type: "transfer" as const, product: "Projecteurs Epson", quantity: 5, user: "Paul Biya", warehouse: "Principal → Campus B", time: "Il y a 5h" },
  { id: "4", type: "inventory" as const, product: "Salle informatique B", user: "Admin", time: "Il y a 1j" },
  { id: "5", type: "maintenance" as const, product: "Climatiseur Labo Chimie", user: "Tech. Maintenance", time: "Il y a 2j" },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-sm text-gray-500 mt-1">
            Vue d'ensemble de la gestion de stock - IUC
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            Cette semaine
          </Button>
          <Button variant="default" size="sm">
            Exporter
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KPICard
          title="Produits en stock"
          value={formatNumber(mockKPIs.totalProducts.value)}
          change={mockKPIs.totalProducts.change}
          trend={mockKPIs.totalProducts.trend}
          icon={Package}
        />
        <KPICard
          title="Valeur du stock"
          value={mockKPIs.stockValue.value}
          change={mockKPIs.stockValue.change}
          trend={mockKPIs.stockValue.trend}
          icon={DollarSign}
          iconColor="text-green-600"
          iconBg="bg-green-50"
        />
        <KPICard
          title="Commandes en cours"
          value={mockKPIs.pendingOrders.value}
          change={mockKPIs.pendingOrders.change}
          trend={mockKPIs.pendingOrders.trend}
          icon={ShoppingCart}
          iconColor="text-yellow-600"
          iconBg="bg-yellow-50"
        />
        <KPICard
          title="Produits en alerte"
          value={mockKPIs.lowStockItems.value}
          change={mockKPIs.lowStockItems.change}
          trend={mockKPIs.lowStockItems.trend}
          icon={AlertTriangle}
          iconColor="text-red-600"
          iconBg="bg-red-50"
        />
        <KPICard
          title="Transferts actifs"
          value={mockKPIs.activeTransfers.value}
          change={mockKPIs.activeTransfers.change}
          trend={mockKPIs.activeTransfers.trend}
          icon={ArrowUpDown}
          iconColor="text-blue-600"
          iconBg="bg-blue-50"
        />
        <KPICard
          title="Fournisseurs"
          value={mockKPIs.totalSuppliers.value}
          change={mockKPIs.totalSuppliers.change}
          trend={mockKPIs.totalSuppliers.trend}
          icon={Users}
          iconColor="text-purple-600"
          iconBg="bg-purple-50"
        />
      </div>

      {/* Graphiques principaux */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Consommation mensuelle */}
        <div className="lg:col-span-2">
          <BaseChart
            title="Consommation mensuelle par catégorie"
            description="Évolution sur 12 mois (en XAF)"
            height={350}
          >
            <BarChart
              data={monthlyConsumption}
              xAxisKey="month"
              bars={[
                { dataKey: "Informatique", name: "Informatique", color: "#1e40af" },
                { dataKey: "Bureautique", name: "Bureautique", color: "#166534" },
                { dataKey: "Laboratoire", name: "Laboratoire", color: "#ca8a04" },
              ]}
            />
          </BaseChart>
        </div>

        {/* Répartition par catégorie */}
        <div>
          <BaseChart
            title="Valeur du stock par catégorie"
            description="Répartition en XAF"
            height={350}
          >
            <PieChart data={stockByCategory} donut={true} />
          </BaseChart>
        </div>
      </div>

      {/* Top produits + Activités */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top produits */}
        <BaseChart
          title="Top 5 des produits en valeur"
          description="Valeur totale en stock"
          height={300}
        >
          <BarChart
            data={topProducts}
            xAxisKey="name"
            layout="vertical"
            bars={[
              { dataKey: "value", name: "Valeur (XAF)", color: "#1e40af" },
            ]}
            showLegend={false}
          />
        </BaseChart>

        {/* Activités récentes */}
        <RecentActivity
          activities={mockActivities}
          onViewAll={() => console.log("Voir tout")}
        />
      </div>
    </div>
  )
}
