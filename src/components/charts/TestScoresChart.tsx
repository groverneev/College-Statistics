"use client";

import { TestScoresData } from "@/lib/types";
import { formatPercent } from "@/utils/dataHelpers";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

interface TestScoresChartProps {
  data: TestScoresData;
  schoolColor?: string;
}

export default function TestScoresChart({
  data,
  schoolColor = "#4E3629",
}: TestScoresChartProps) {
  const satData = data.sat
    ? [
        {
          name: "ERW",
          p25: data.sat.readingWriting.p25,
          p50: data.sat.readingWriting.p50,
          p75: data.sat.readingWriting.p75,
          range: data.sat.readingWriting.p75 - data.sat.readingWriting.p25,
        },
        {
          name: "Math",
          p25: data.sat.math.p25,
          p50: data.sat.math.p50,
          p75: data.sat.math.p75,
          range: data.sat.math.p75 - data.sat.math.p25,
        },
      ]
    : [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Test Scores (25th-75th Percentile)</h3>

      {data.sat && (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-sm font-medium text-gray-600 dark:text-gray-300">
              SAT Scores
            </h4>
            <span className="text-xs text-gray-500">
              {formatPercent(data.sat.submissionRate)} submitted
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold" style={{ color: schoolColor }}>
                {data.sat.composite.p25}-{data.sat.composite.p75}
              </div>
              <div className="text-sm text-gray-500">Composite Range</div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold">{data.sat.composite.p50}</div>
              <div className="text-sm text-gray-500">Median</div>
            </div>
          </div>

          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={satData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                <XAxis type="number" domain={[600, 800]} />
                <YAxis type="category" dataKey="name" width={50} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-white p-2 border border-gray-200 rounded shadow-sm">
                          <p className="font-medium">{d.name}</p>
                          <p className="text-sm">Range: {d.p25} - {d.p75}</p>
                          <p className="text-sm">Median: {d.p50}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="p25" stackId="a" fill="transparent" />
                <Bar dataKey="range" stackId="a" fill={schoolColor} radius={[0, 4, 4, 0]}>
                  {satData.map((_, index) => (
                    <Cell key={`cell-${index}`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {data.act && (
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-sm font-medium text-gray-600 dark:text-gray-300">
              ACT Composite
            </h4>
            <span className="text-xs text-gray-500">
              {formatPercent(data.act.submissionRate)} submitted
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div
              className="text-2xl font-bold"
              style={{ color: schoolColor }}
            >
              {data.act.composite.p25}-{data.act.composite.p75}
            </div>
            <div className="text-sm text-gray-500">
              (Median: {data.act.composite.p50})
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
