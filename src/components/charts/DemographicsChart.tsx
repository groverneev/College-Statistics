"use client";

import { DemographicsData } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

interface DemographicsChartProps {
  data: DemographicsData;
  schoolColor?: string;
}

const RACE_COLORS = {
  white: "#6B7280",
  asian: "#3B82F6",
  hispanicLatino: "#F59E0B",
  blackAfricanAmerican: "#10B981",
  international: "#8B5CF6",
  twoOrMoreRaces: "#EC4899",
  unknown: "#9CA3AF",
  americanIndianAlaskaNative: "#EF4444",
  nativeHawaiianPacificIslander: "#14B8A6",
};

const RACE_LABELS: Record<string, string> = {
  white: "White",
  asian: "Asian",
  hispanicLatino: "Hispanic/Latino",
  blackAfricanAmerican: "Black/African American",
  international: "International",
  twoOrMoreRaces: "Two or More Races",
  unknown: "Unknown",
  americanIndianAlaskaNative: "American Indian/Alaska Native",
  nativeHawaiianPacificIslander: "Native Hawaiian/Pacific Islander",
};

export default function DemographicsChart({
  data,
  schoolColor = "#4E3629",
}: DemographicsChartProps) {
  const total = data.enrollment.undergraduate;

  const raceData = Object.entries(data.byRace)
    .map(([key, value]) => ({
      name: RACE_LABELS[key] || key,
      value,
      percent: total > 0 ? (value / total) * 100 : 0,
      color: RACE_COLORS[key as keyof typeof RACE_COLORS] || "#6B7280",
    }))
    .filter((d) => d.value > 0)
    .sort((a, b) => b.value - a.value);

  const residencyData = [
    { name: "Out of State", value: data.byResidency.outOfState },
    { name: "International", value: data.byResidency.international },
    { name: "In State", value: data.byResidency.inState },
  ].filter((d) => d.value > 0);

  const RESIDENCY_COLORS = [schoolColor, `${schoolColor}99`, `${schoolColor}55`];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Student Demographics</h3>

      <div className="text-center mb-4">
        <div className="text-2xl font-bold" style={{ color: schoolColor }}>
          {formatNumber(data.enrollment.undergraduate)}
        </div>
        <div className="text-sm text-gray-500">Undergraduate Students</div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">
          By Race/Ethnicity
        </h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={raceData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
              <XAxis
                type="number"
                tickFormatter={(v) => `${v.toFixed(0)}%`}
                domain={[0, "auto"]}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={140}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(value, _name, props) => {
                  const v = value as number;
                  const payload = props as { payload: { value: number } };
                  return [`${v.toFixed(1)}% (${formatNumber(payload.payload.value)})`, ""];
                }}
                labelFormatter={() => ""}
              />
              <Bar dataKey="percent" radius={[0, 4, 4, 0]}>
                {raceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-3">
          By Residency
        </h4>
        <div className="h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={residencyData}
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={50}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                }
                labelLine={false}
              >
                {residencyData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={RESIDENCY_COLORS[index]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => formatNumber(value as number)}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
