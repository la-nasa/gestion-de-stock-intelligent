"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowRight, Package, ShoppingCart, ArrowRightLeft, ClipboardList, Wrench } from "lucide-react"

interface Activity {
  id: string
  type: "entry" | "output" | "transfer" | "inventory" | "maintenance"
  product: string
  quantity?: number
  user: string
  warehouse?: string
  time: string
}

const activityIcons = {
  entry: { icon: Package, color: "bg-green-50 text-green-600" },
  output: { icon: ShoppingCart, color: "bg-red-50 text-red-600" },
  transfer: { icon: ArrowRightLeft, color: "bg-blue-50 text-blue-600" },
  inventory: { icon: ClipboardList, color: "bg-yellow-50 text-yellow-600" },
  maintenance: { icon: Wrench, color: "bg-purple-50 text-purple-600" },
}

const activityLabels = {
  entry: "Entrée",
  output: "Sortie",
  transfer: "Transfert",
  inventory: "Inventaire",
  maintenance: "Maintenance",
}

interface RecentActivityProps {
  activities: Activity[]
  onViewAll?: () => void
}

export function RecentActivity({ activities, onViewAll }: RecentActivityProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base font-semibold">
          Activités récentes
        </CardTitle>
        {onViewAll && (
          <Button variant="ghost" size="sm" onClick={onViewAll}>
            Voir tout
            <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {activities.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 text-sm">Aucune activité récente</p>
            </div>
          ) : (
            activities.slice(0, 8).map((activity) => {
              const config = activityIcons[activity.type]
              const Icon = config.icon
              return (
                <div
                  key={activity.id}
                  className="flex items-center gap-4 px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className={`p-2 rounded-lg ${config.color}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {activityLabels[activity.type]}
                      </Badge>
                      <span className="text-sm font-medium text-gray-900 truncate">
                        {activity.product}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {activity.quantity && `Qté: ${activity.quantity} • `}
                      Par {activity.user}
                      {activity.warehouse && ` • ${activity.warehouse}`}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400 flex-shrink-0">
                    {activity.time}
                  </span>
                </div>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
