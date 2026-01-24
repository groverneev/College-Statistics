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
  Legend,
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

  const trendData = years.map((year) => ({
    year: year.split("-")[0],
    fullYear: year,
    tuition: yearData[year].costs.tuition,
    fees: yearData[year].costs.fees,
    roomAndBoard: yearData[year].costs.roomAndBoard,
    total: yearData[year].costs.totalCOA,
  }));

  const latestData = trendData[trendData.length - 1];
  const earliestData = trendData[0];
  const costIncrease = ((latestData.total - earliestData.total) / earliestData.total) * 100;

  return (
    <div className="card p-6">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Cost of Attendance Over Time
        </h3>
        <div className="text-right">
          <div className="text-2xl font-bold" style={{ color: schoolColor }}>
            {formatCurrency(latestData.total)}
          </div>
          <div className="text-xs text-gray-500">
            {latestData.fullYear} Total COA
          </div>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis
              dataKey="year"
              tick={{ fontSize: 12, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#666" }}
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
            <Legend
              formatter={(value) =>
                value === "tuition" ? "Tuition" : value === "fees" ? "Fees" : "Room & Board"
              }
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

      {/* Cost breakdown */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-4 gap-4 text-center text-sm">
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
