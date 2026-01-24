"use client";

import { YearData } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/utils/dataHelpers";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface FinancialAidTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

export default function FinancialAidTrendChart({
  yearData,
  schoolColor,
}: FinancialAidTrendChartProps) {
  const years = Object.keys(yearData).sort();

  const trendData = years.map((year) => ({
    year: year.split("-")[0],
    fullYear: year,
    percentReceivingAid: yearData[year].financialAid.percentReceivingAid * 100,
    averageAidPackage: yearData[year].financialAid.averageAidPackage,
    averageNeedBasedGrant: yearData[year].financialAid.averageNeedBasedGrant,
    percentNeedFullyMet: yearData[year].financialAid.percentNeedFullyMet * 100,
    averageNetPrice: yearData[year].financialAid.averageNetPrice || 0,
    totalCOA: yearData[year].costs.totalCOA,
  }));

  const latestData = trendData[trendData.length - 1];

  return (
    <div className="card p-6 h-full">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        Financial Aid Overview
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={trendData}>
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
                name === "totalCOA" ? "Total Cost" : "Avg Aid Package",
              ]}
              labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
            />
            <Legend
              formatter={(value) =>
                value === "totalCOA" ? "Total Cost" : "Avg Aid Package"
              }
            />
            <Bar
              dataKey="totalCOA"
              fill="#e5e5e5"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="averageAidPackage"
              fill="#27ae60"
              radius={[4, 4, 0, 0]}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Key stats */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-center text-sm">
          <div>
            <div className="text-gray-500">Students Receiving Aid</div>
            <div className="font-semibold text-lg" style={{ color: schoolColor }}>
              {latestData.percentReceivingAid.toFixed(0)}%
            </div>
          </div>
          <div>
            <div className="text-gray-500">Need Fully Met</div>
            <div className="font-semibold text-lg text-green-600">
              {latestData.percentNeedFullyMet.toFixed(0)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
