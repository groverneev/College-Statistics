"use client";

import { YearData } from "@/lib/types";
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
  Cell,
} from "recharts";

interface TestScoresTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

export default function TestScoresTrendChart({
  yearData,
  schoolColor,
}: TestScoresTrendChartProps) {
  const years = Object.keys(yearData).sort();

  const satTrendData = years
    .filter((year) => yearData[year].testScores.sat)
    .map((year) => {
      const sat = yearData[year].testScores.sat!;
      return {
        year: year.split("-")[0],
        fullYear: year,
        p25: sat.composite.p25,
        p50: sat.composite.p50,
        p75: sat.composite.p75,
        // For stacked bar: bottom portion and middle range
        bottom: sat.composite.p25,
        middle: sat.composite.p50 - sat.composite.p25,
        top: sat.composite.p75 - sat.composite.p50,
      };
    });

  if (satTrendData.length === 0) {
    return null;
  }

  return (
    <div className="card p-6 h-full">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        SAT Score Trends (Middle 50%)
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={satTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis
              dataKey="year"
              tick={{ fontSize: 12, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
            />
            <YAxis
              domain={[1400, 1600]}
              tick={{ fontSize: 12, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
              label={{
                value: "SAT Score",
                angle: -90,
                position: "insideLeft",
                style: { textAnchor: "middle", fill: "#666", fontSize: 12 },
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e5e5",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                      <p className="font-semibold text-gray-800">{d.fullYear}</p>
                      <p className="text-sm text-gray-600">75th: {d.p75}</p>
                      <p className="text-sm text-gray-600">50th: {d.p50}</p>
                      <p className="text-sm text-gray-600">25th: {d.p25}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              formatter={(value) => {
                if (value === "p75") return "75th Percentile";
                if (value === "p50") return "50th Percentile";
                if (value === "p25") return "25th Percentile";
                return value;
              }}
            />
            <Bar dataKey="bottom" stackId="a" fill="transparent" />
            <Bar
              dataKey="middle"
              stackId="a"
              fill={schoolColor}
              fillOpacity={0.5}
              name="p25"
            />
            <Bar
              dataKey="top"
              stackId="a"
              fill="#27ae60"
              fillOpacity={0.7}
              name="p75"
              radius={[4, 4, 0, 0]}
            />
            <Line
              type="monotone"
              dataKey="p50"
              stroke="#2980b9"
              strokeWidth={3}
              dot={{ fill: "#2980b9", r: 4 }}
              name="p50"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Simple data summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <div className="text-gray-500">25th Percentile</div>
            <div className="font-semibold" style={{ color: schoolColor }}>
              {satTrendData[satTrendData.length - 1]?.p25}
            </div>
          </div>
          <div>
            <div className="text-gray-500">50th Percentile</div>
            <div className="font-semibold text-blue-600">
              {satTrendData[satTrendData.length - 1]?.p50}
            </div>
          </div>
          <div>
            <div className="text-gray-500">75th Percentile</div>
            <div className="font-semibold text-green-600">
              {satTrendData[satTrendData.length - 1]?.p75}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
