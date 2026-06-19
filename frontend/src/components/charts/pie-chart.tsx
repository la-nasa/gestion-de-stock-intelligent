"use client"

import React from "react"
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts"

interface PieChartProps {
  data: {
    name: string
    value: number
    color: string
  }[]
  innerRadius?: number
  outerRadius?: number
  showLegend?: boolean
  donut?: boolean
}

const COLORS = [
  "#1e40af", "#166534", "#ca8a04", "#dc2626",
  "#7c3aed", "#0891b2", "#be123c", "#4f46e5",
  "#059669", "#d97706", "#2563eb", "#9333ea",
]

export function PieChart({
  data,
  innerRadius = 60,
  outerRadius = 80,
  showLegend = true,
  donut = true,
}: PieChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          innerRadius={donut ? innerRadius : 0}
          outerRadius={outerRadius}
          fill="#8884d8"
          dataKey="value"
          paddingAngle={2}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.color || COLORS[index % COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "white",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
            fontSize: "12px",
          }}
          formatter={(value: number) => [`${value.toLocaleString()}`, ""]}
        />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: "12px" }}
            iconType="circle"
            iconSize={8}
          />
        )}
      </RechartsPieChart>
    </ResponsiveContainer>
  )
}
