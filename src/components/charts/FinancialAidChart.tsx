"use client";

import { FinancialAidData, CostsData } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/utils/dataHelpers";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface FinancialAidChartProps {
  data: FinancialAidData;
  costs?: CostsData;
  schoolColor?: string;
}

export default function FinancialAidChart({
  data,
  costs,
  schoolColor = "#4E3629",
}: FinancialAidChartProps) {
  const aidPieData = [
    { name: "Receiving Aid", value: data.percentReceivingAid * 100 },
    { name: "Not Receiving Aid", value: (1 - data.percentReceivingAid) * 100 },
  ];

  const needMetPieData = [
    { name: "Need Fully Met", value: data.percentNeedFullyMet * 100 },
    { name: "Need Partially Met", value: (1 - data.percentNeedFullyMet) * 100 },
  ];

  const COLORS = [schoolColor, "#e5e7eb"];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Financial Aid</h3>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className="h-24">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={aidPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={25}
                  outerRadius={40}
                  dataKey="value"
                  startAngle={90}
                  endAngle={-270}
                >
                  {aidPieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => `${(value as number).toFixed(0)}%`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-xl font-bold" style={{ color: schoolColor }}>
            {formatPercent(data.percentReceivingAid)}
          </div>
          <div className="text-xs text-gray-500">Receive Aid</div>
        </div>

        <div className="text-center">
          <div className="h-24">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={needMetPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={25}
                  outerRadius={40}
                  dataKey="value"
                  startAngle={90}
                  endAngle={-270}
                >
                  {needMetPieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => `${(value as number).toFixed(0)}%`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-xl font-bold" style={{ color: schoolColor }}>
            {formatPercent(data.percentNeedFullyMet)}
          </div>
          <div className="text-xs text-gray-500">Need Fully Met</div>
        </div>
      </div>

      <div className="space-y-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-300">
            Average Aid Package
          </span>
          <span className="font-semibold">{formatCurrency(data.averageAidPackage)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-300">
            Average Need-Based Grant
          </span>
          <span className="font-semibold">{formatCurrency(data.averageNeedBasedGrant)}</span>
        </div>
        {data.averageNetPrice && costs && (
          <div className="flex justify-between pt-2 border-t border-gray-100 dark:border-gray-600">
            <span className="text-sm text-gray-600 dark:text-gray-300">
              Average Net Price
            </span>
            <span className="font-semibold" style={{ color: schoolColor }}>
              {formatCurrency(data.averageNetPrice)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
