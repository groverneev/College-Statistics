"use client";

import { YearData } from "@/lib/types";
import { formatNumber } from "@/utils/dataHelpers";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface DemographicsTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

const RACE_COLORS: Record<string, string> = {
  white: "#95a5a6",
  asian: "#3498db",
  hispanicLatino: "#e67e22",
  blackAfricanAmerican: "#27ae60",
  international: "#9b59b6",
  twoOrMoreRaces: "#e74c3c",
  unknown: "#bdc3c7",
};

const RACE_LABELS: Record<string, string> = {
  white: "White",
  asian: "Asian",
  hispanicLatino: "Hispanic/Latino",
  blackAfricanAmerican: "Black/African American",
  international: "International",
  twoOrMoreRaces: "Two or More",
  unknown: "Unknown",
};

export default function DemographicsTrendChart({
  yearData,
  schoolColor,
}: DemographicsTrendChartProps) {
  const years = Object.keys(yearData).sort();
  const latestYear = years[years.length - 1];
  const latestDemo = yearData[latestYear].demographics;
  const totalUndergrad = latestDemo.enrollment.undergraduate;

  // Enrollment trend data
  const enrollmentData = years.map((year) => ({
    year: year.split("-")[0],
    fullYear: year,
    undergraduate: yearData[year].demographics.enrollment.undergraduate,
    graduate: yearData[year].demographics.enrollment.graduate || 0,
  }));

  // Pie chart data for current demographics
  const pieData = Object.entries(latestDemo.byRace)
    .filter(([key]) => key in RACE_LABELS && latestDemo.byRace[key as keyof typeof latestDemo.byRace] > 0)
    .map(([key, value]) => ({
      name: RACE_LABELS[key],
      value,
      percent: totalUndergrad > 0 ? (value / totalUndergrad) * 100 : 0,
      color: RACE_COLORS[key],
    }))
    .sort((a, b) => b.value - a.value);

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        Student Demographics
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Enrollment Trend */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">
            Enrollment Over Time
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={enrollmentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis
                  dataKey="year"
                  tick={{ fontSize: 12, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                  tickFormatter={(v) => formatNumber(v)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "white",
                    border: "1px solid #e5e5e5",
                    borderRadius: "8px",
                  }}
                  formatter={(value) => [formatNumber(value as number), ""]}
                  labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="undergraduate"
                  name="Undergraduate"
                  stroke={schoolColor}
                  strokeWidth={3}
                  dot={{ fill: schoolColor, r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="graduate"
                  name="Graduate"
                  stroke="#27ae60"
                  strokeWidth={2}
                  dot={{ fill: "#27ae60", r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Demographics Pie Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">
            Current Demographics ({latestYear})
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent ?? 0).toFixed(0)}%`}
                  labelLine={false}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [formatNumber(value as number), "Students"]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
          <div>
            <div className="text-gray-500">Undergraduates</div>
            <div className="font-semibold text-lg" style={{ color: schoolColor }}>
              {formatNumber(latestDemo.enrollment.undergraduate)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">Total Enrollment</div>
            <div className="font-semibold text-lg">
              {formatNumber(latestDemo.enrollment.total)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">International</div>
            <div className="font-semibold text-lg text-purple-600">
              {((latestDemo.byRace.international / totalUndergrad) * 100).toFixed(0)}%
            </div>
          </div>
          <div>
            <div className="text-gray-500">Students of Color</div>
            <div className="font-semibold text-lg text-green-600">
              {(100 - (latestDemo.byRace.white / totalUndergrad) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
