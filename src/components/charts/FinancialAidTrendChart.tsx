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

  const trendData = years
    .filter((year) => {
      const aid = yearData[year].financialAid;
      return (
        (aid.percentReceivingAid ?? 0) > 0 ||
        (aid.averageAidPackage ?? 0) > 0 ||
        (aid.averageNeedBasedGrant ?? 0) > 0 ||
        (aid.percentNeedFullyMet ?? 0) > 0
      );
    })
    .map((year) => ({
      year: year.split("-")[0],
      fullYear: year,
      percentReceivingAid: (yearData[year].financialAid.percentReceivingAid ?? 0) * 100,
      averageAidPackage: yearData[year].financialAid.averageAidPackage ?? 0,
      averageNeedBasedGrant: yearData[year].financialAid.averageNeedBasedGrant ?? 0,
      percentNeedFullyMet: (yearData[year].financialAid.percentNeedFullyMet ?? 0) * 100,
      averageNetPrice: yearData[year].financialAid.averageNetPrice || 0,
      totalCOA: yearData[year].costs.totalCOA,
    }));

  if (trendData.length === 0) {
    return null;
  }

  const latestData = trendData[trendData.length - 1];

  return (
    <div className="card p-4 sm:p-6 h-full min-w-0">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        Financial Aid Overview
      </h3>
      <div className="h-64">
        <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height="100%">
          <ComposedChart data={trendData}>
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
                name === "totalCOA" ? "Total Cost" : "Avg Aid Package",
              ]}
              labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
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
      <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs text-gray-600">
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-green-600" />Avg Aid Package</span>
        <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-gray-200" />Total Cost</span>
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
