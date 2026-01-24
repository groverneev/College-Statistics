"use client";

import { AdmissionsData } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";

interface AdmissionsChartProps {
  data: AdmissionsData;
  schoolColor?: string;
}

export default function AdmissionsChart({
  data,
  schoolColor = "#4E3629",
}: AdmissionsChartProps) {
  const chartData = [
    {
      name: "Applied",
      value: data.applied,
      fill: schoolColor,
      opacity: 0.4,
    },
    {
      name: "Admitted",
      value: data.admitted,
      fill: schoolColor,
      opacity: 0.7,
    },
    {
      name: "Enrolled",
      value: data.enrolled,
      fill: schoolColor,
      opacity: 1,
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-2">Admissions Funnel</h3>
      <div className="grid grid-cols-3 gap-4 mb-4 text-center">
        <div>
          <div className="text-2xl font-bold">{formatPercent(data.acceptanceRate)}</div>
          <div className="text-sm text-gray-500">Acceptance Rate</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{formatPercent(data.yield)}</div>
          <div className="text-sm text-gray-500">Yield</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{formatNumber(data.enrolled)}</div>
          <div className="text-sm text-gray-500">Class Size</div>
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
            <XAxis type="number" tickFormatter={(v) => formatNumber(v)} />
            <YAxis type="category" dataKey="name" width={80} />
            <Tooltip
              formatter={(value) => formatNumber(value as number)}
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "6px",
              }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.fill}
                  fillOpacity={entry.opacity}
                />
              ))}
              <LabelList
                dataKey="value"
                position="right"
                formatter={(v) => formatNumber(v as number)}
                className="text-sm"
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {data.earlyDecision && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">
            Early Decision
          </h4>
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-gray-500">Applied:</span>{" "}
              <span className="font-medium">{formatNumber(data.earlyDecision.applied)}</span>
            </div>
            <div>
              <span className="text-gray-500">Admitted:</span>{" "}
              <span className="font-medium">{formatNumber(data.earlyDecision.admitted)}</span>
            </div>
            <div>
              <span className="text-gray-500">Rate:</span>{" "}
              <span className="font-medium">
                {formatPercent(data.earlyDecision.admitted / data.earlyDecision.applied)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
