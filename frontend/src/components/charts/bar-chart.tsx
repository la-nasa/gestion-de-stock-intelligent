"use client"

import React from "react"
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"

interface BarChartProps {
  data: any[]
  bars: {
    dataKey: string
    name: string
    color: string
    stackId?: string
  }[]
  xAxisKey: string
  showGrid?: boolean
  showLegend?: boolean
  layout?: "horizontal" | "vertical"
}

export function BarChart({
  data,
  bars,
  xAxisKey,
  showGrid = true,
  showLegend = true,
  layout = "horizontal",
}: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RechartsBarChart
        data={data}
        layout={layout}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        {showGrid && (
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#f0f0f0"
            vertical={false}
          />
        )}
        <XAxis
          dataKey={xAxisKey}
          type={layout === "horizontal" ? "category" : "number"}
          tick={{ fontSize: 12, fill: "#6b7280" }}
          axisLine={{ stroke: "#e5e7eb" }}
          tickLine={false}
        />
        <YAxis
          type={layout === "horizontal" ? "number" : "category"}
          tick={{ fontSize: 12, fill: "#6b7280" }}
          axisLine={{ stroke: "#e5e7eb" }}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "white",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
            fontSize: "12px",
          }}
        />
        {showLegend && (
          <Legend
            wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }}
          />
        )}
        {bars.map((bar) => (
          <Bar
            key={bar.dataKey}
            dataKey={bar.dataKey}
            name={bar.name}
            fill={bar.color}
            stackId={bar.stackId}
            radius={[4, 4, 0, 0]}
            maxBarSize={40}
          />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  )
}
