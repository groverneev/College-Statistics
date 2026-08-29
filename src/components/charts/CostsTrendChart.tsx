"use client";

import { YearData } from "@/lib/types";
import { formatCurrency } from "@/utils/dataHelpers";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface CostsTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

export default function CostsTrendChart({
  yearData,
  schoolColor,
}: CostsTrendChartProps) {
  const years = Object.keys(yearData).sort();

  const trendData = years
    .filter((year) => {
      const costs = yearData[year].costs;
      return (
        typeof costs.tuition === "number" &&
        typeof costs.fees === "number" &&
        typeof costs.roomAndBoard === "number" &&
        typeof costs.totalCOA === "number" &&
        costs.totalCOA > 0
      );
    })
    .map((year) => ({
      year: year.split("-")[0],
      fullYear: year,
      tuition: yearData[year].costs.tuition!,
      fees: yearData[year].costs.fees!,
      roomAndBoard: yearData[year].costs.roomAndBoard!,
      total: yearData[year].costs.totalCOA!,
    }));

  if (trendData.length === 0) {
    return null;
  }

  const latestData = trendData[trendData.length - 1];
  const earliestData = trendData[0];
  const costIncrease = ((latestData.total - earliestData.total) / earliestData.total) * 100;

  return (
    <div className="card p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Cost of Attendance Over Time
        </h3>
        <div className="text-left sm:text-right">
          <div className="text-2xl font-bold" style={{ color: schoolColor }}>
            {formatCurrency(latestData.total)}
          </div>
          <div className="text-xs text-gray-500">
            {latestData.fullYear} Total COA
          </div>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height="100%">
          <AreaChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis
              dataKey="year"
              tick={{ fontSize: 12, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
            />
            <YAxis
              width={44}
              tick={{ fontSize: 10, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e5e5",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              }}
              formatter={(value, name) => [
                formatCurrency(value as number),
                name === "tuition" ? "Tuition" : name === "fees" ? "Fees" : "Room & Board",
              ]}
              labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
            />
            <Area
              type="monotone"
              dataKey="tuition"
              stackId="1"
              stroke={schoolColor}
              fill={schoolColor}
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="fees"
              stackId="1"
              stroke="#e67e22"
              fill="#e67e22"
              fillOpacity={0.8}
            />
            <Area
              type="monotone"
              dataKey="roomAndBoard"
              stackId="1"
              stroke="#27ae60"
              fill="#27ae60"
              fillOpacity={0.8}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs text-gray-600">
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: schoolColor }} />Tuition</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-orange-500" />Fees</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-green-600" />Room &amp; Board</span>
      </div>

      {/* Cost breakdown */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center text-sm">
          <div>
            <div className="text-gray-500">Tuition</div>
            <div className="font-semibold" style={{ color: schoolColor }}>
              {formatCurrency(latestData.tuition)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">Fees</div>
            <div className="font-semibold text-orange-500">
              {formatCurrency(latestData.fees)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">Room & Board</div>
            <div className="font-semibold text-green-600">
              {formatCurrency(latestData.roomAndBoard)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">Change Since {earliestData.year}</div>
            <div className="font-semibold text-red-500">
              +{costIncrease.toFixed(0)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
