"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface BaseChartProps {
  title: string
  description?: string
  children: React.ReactNode
  className?: string
  action?: React.ReactNode
  height?: number
}

export function BaseChart({
  title,
  description,
  children,
  className,
  action,
  height = 300,
}: BaseChartProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-base font-semibold">{title}</CardTitle>
          {description && (
            <p className="text-xs text-gray-500 mt-0.5">{description}</p>
          )}
        </div>
        {action}
      </CardHeader>
      <CardContent>
        <div style={{ height: `${height}px` }} className="w-full">
          {children}
        </div>
      </CardContent>
    </Card>
  )
}
