"use client"

import React from "react"
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Area,
  AreaChart,
} from "recharts"

interface LineChartProps {
  data: any[]
  lines: {
    dataKey: string
    name: string
    color: string
    strokeWidth?: number
    area?: boolean
  }[]
  xAxisKey: string
  showGrid?: boolean
  showLegend?: boolean
  showArea?: boolean
}

export function LineChart({
  data,
  lines,
  xAxisKey,
  showGrid = true,
  showLegend = true,
  showArea = false,
}: LineChartProps) {
  const ChartComponent = showArea ? AreaChart : RechartsLineChart

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ChartComponent
        data={data}
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
          tick={{ fontSize: 12, fill: "#6b7280" }}
          axisLine={{ stroke: "#e5e7eb" }}
          tickLine={false}
        />
        <YAxis
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
        {lines.map((line) =>
          showArea ? (
            <Area
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              name={line.name}
              stroke={line.color}
              fill={line.color}
              fillOpacity={0.1}
              strokeWidth={line.strokeWidth || 2}
            />
          ) : (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              name={line.name}
              stroke={line.color}
              strokeWidth={line.strokeWidth || 2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 2 }}
            />
          )
        )}
      </ChartComponent>
    </ResponsiveContainer>
  )
}
