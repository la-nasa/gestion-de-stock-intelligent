"use client"

import React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, type LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface KPICardProps {
  title: string
  value: string | number
  description?: string
  change?: string
  trend?: "up" | "down" | "neutral"
  icon: LucideIcon
  iconColor?: string
  iconBg?: string
  className?: string
  onClick?: () => void
}

export function KPICard({
  title,
  value,
  description,
  change,
  trend,
  icon: Icon,
  iconColor = "text-primary-600",
  iconBg = "bg-primary-50",
  className,
  onClick,
}: KPICardProps) {
  return (
    <Card
      className={cn(
        "transition-all duration-200 hover:shadow-soft-lg cursor-pointer animate-slide-up",
        className
      )}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className={cn("p-2.5 rounded-xl", iconBg)}>
            <Icon className={cn("h-5 w-5", iconColor)} />
          </div>
          {change && trend && (
            <Badge
              variant={
                trend === "up" ? "success" : trend === "down" ? "danger" : "secondary"
              }
              className="text-xs"
            >
              {trend === "up" ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : trend === "down" ? (
                <TrendingDown className="h-3 w-3 mr-1" />
              ) : null}
              {change}
            </Badge>
          )}
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900 tracking-tight">
            {value}
          </p>
          <p className="text-sm font-medium text-gray-600 mt-1">{title}</p>
          {description && (
            <p className="text-xs text-gray-400 mt-1">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
