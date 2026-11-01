"use client";

import { useState } from "react";
import type { YearData } from "@/lib/types";
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface TestScoresTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

type Percentiles = { p25?: number; p50?: number; p75?: number };
type SatView = "composite" | "sections";

const READING_COLOR = "#2980b9";
const MATH_COLOR = "#e67e22";

function hasRange(p: Percentiles | undefined): p is Percentiles & { p25: number; p75: number } {
  return typeof p?.p25 === "number" && typeof p.p75 === "number";
}

function axisMin(scores: (number | undefined)[]) {
  const reported = scores.filter((score): score is number => typeof score === "number");
  return Math.floor(Math.min(...reported) / 50) * 50 - 50;
}

export default function TestScoresTrendChart({ yearData, schoolColor }: TestScoresTrendChartProps) {
  const years = Object.keys(yearData).sort();

  const satTrendData = years
    .filter((year) => hasRange(yearData[year].testScores.sat?.composite))
    .map((year) => {
      const composite = yearData[year].testScores.sat!.composite!;
      return {
        year: year.split("-")[0],
        fullYear: year,
        p25: composite.p25!,
        p50: composite.p50,
        p75: composite.p75!,
        range: [composite.p25!, composite.p75!],
      };
    });

  // Many schools report only the two section scores, especially before the CDS added a composite row.
  const sectionTrendData = years
    .filter((year) => {
      const sat = yearData[year].testScores.sat;
      return hasRange(sat?.readingWriting) && hasRange(sat?.math);
    })
    .map((year) => {
      const sat = yearData[year].testScores.sat!;
      const rw = sat.readingWriting!;
      const math = sat.math!;
      return {
        year: year.split("-")[0],
        fullYear: year,
        rw: { p25: rw.p25!, p50: rw.p50, p75: rw.p75! },
        math: { p25: math.p25!, p50: math.p50, p75: math.p75! },
        rwRange: [rw.p25!, rw.p75!],
        mathRange: [math.p25!, math.p75!],
      };
    });

  const latestCompositeYear = satTrendData[satTrendData.length - 1]?.fullYear ?? "";
  const latestSectionYear = sectionTrendData[sectionTrendData.length - 1]?.fullYear ?? "";
  const [view, setView] = useState<SatView>(
    latestSectionYear > latestCompositeYear ? "sections" : "composite",
  );

  if (satTrendData.length === 0 && sectionTrendData.length === 0) {
    return null;
  }
  const canToggle = satTrendData.length > 0 && sectionTrendData.length > 0;
  const activeView: SatView = satTrendData.length === 0 ? "sections" : sectionTrendData.length === 0 ? "composite" : view;
  const hasReportedMedian = satTrendData.some((point) => point.p50 != null);
  const latestSections = sectionTrendData[sectionTrendData.length - 1];

  const tooltipStyle = {
    backgroundColor: "white",
    border: "1px solid #e5e5e5",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  };

  const formatRange = (p: Percentiles) => `${p.p25}-${p.p75}`;

  return (
    <div className="card p-4 sm:p-6 h-full min-w-0">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-lg font-semibold text-gray-800">SAT Score Trends (Middle 50%)</h3>
        {canToggle && (
          <div className="inline-flex rounded-lg border border-gray-200 p-0.5 text-xs font-medium">
            {(
              [
                ["composite", "Total"],
                ["sections", "Sections"],
              ] as const
            ).map(([option, label]) => (
              <button
                key={option}
                type="button"
                aria-pressed={activeView === option}
                onClick={() => setView(option)}
                className="min-h-8 rounded-md px-3 transition-colors"
                style={
                  activeView === option
                    ? { backgroundColor: schoolColor, color: "#ffffff" }
                    : { color: "#4b5563" }
                }
              >
                {label}
              </button>
            ))}
          </div>
        )}
      </div>

      {activeView === "composite" ? (
        <>
          <div className="h-64">
            <ResponsiveContainer
              initialDimension={{ width: 1, height: 1 }}
              width="100%"
              height="100%"
            >
              <AreaChart data={satTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis
                  dataKey="year"
                  tick={{ fontSize: 12, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                />
                <YAxis
                  width={42}
                  domain={[
                    axisMin(satTrendData.flatMap((point) => [point.p25, point.p50, point.p75])),
                    1600,
                  ]}
                  tick={{ fontSize: 10, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                          <p className="font-semibold text-gray-800">{d.fullYear}</p>
                          <p className="text-sm text-gray-600">75th: {d.p75}</p>
                          {d.p50 != null && (
                            <p className="text-sm text-gray-600">50th: {d.p50}</p>
                          )}
                          <p className="text-sm text-gray-600">25th: {d.p25}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="range"
                  fill={schoolColor}
                  fillOpacity={0.3}
                  stroke={schoolColor}
                  strokeWidth={2}
                  name="range"
                />
                {hasReportedMedian && (
                  <Line
                    type="monotone"
                    dataKey="p50"
                    stroke="#2980b9"
                    strokeWidth={3}
                    dot={{ fill: "#2980b9", r: 5 }}
                    name="p50"
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs text-gray-600">
            {hasReportedMedian && (
              <span className="flex items-center gap-1.5">
                <span className="h-0.5 w-4 bg-blue-600" />
                Median
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <span
                className="h-2.5 w-4 rounded-sm opacity-30"
                style={{ backgroundColor: schoolColor }}
              />
              Middle 50% Range
            </span>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-3 gap-2 sm:gap-4 text-center text-sm">
              <div>
                <div className="text-gray-500">25th Percentile</div>
                <div className="font-semibold" style={{ color: schoolColor }}>
                  {satTrendData[satTrendData.length - 1]?.p25}
                </div>
              </div>
              <div>
                <div className="text-gray-500">50th Percentile</div>
                <div className="font-semibold text-blue-600">
                  {satTrendData[satTrendData.length - 1]?.p50 ?? "Not reported"}
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
        </>
      ) : (
        <>
          <div className="h-64">
            <ResponsiveContainer
              initialDimension={{ width: 1, height: 1 }}
              width="100%"
              height="100%"
            >
              <AreaChart data={sectionTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis
                  dataKey="year"
                  tick={{ fontSize: 12, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                />
                <YAxis
                  width={42}
                  domain={[
                    axisMin(sectionTrendData.flatMap((point) => [point.rw.p25, point.math.p25])),
                    800,
                  ]}
                  tick={{ fontSize: 10, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                          <p className="font-semibold text-gray-800">{d.fullYear}</p>
                          <p className="text-sm text-gray-600">
                            Reading &amp; Writing: {formatRange(d.rw)}
                            {d.rw.p50 != null && ` (median ${d.rw.p50})`}
                          </p>
                          <p className="text-sm text-gray-600">
                            Math: {formatRange(d.math)}
                            {d.math.p50 != null && ` (median ${d.math.p50})`}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="rwRange"
                  fill={READING_COLOR}
                  fillOpacity={0.25}
                  stroke={READING_COLOR}
                  strokeWidth={2}
                  name="rwRange"
                />
                <Area
                  type="monotone"
                  dataKey="mathRange"
                  fill={MATH_COLOR}
                  fillOpacity={0.25}
                  stroke={MATH_COLOR}
                  strokeWidth={2}
                  name="mathRange"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs text-gray-600">
            <span className="flex items-center gap-1.5">
              <span
                className="h-2.5 w-4 rounded-sm opacity-40"
                style={{ backgroundColor: READING_COLOR }}
              />
              Reading &amp; Writing
            </span>
            <span className="flex items-center gap-1.5">
              <span
                className="h-2.5 w-4 rounded-sm opacity-40"
                style={{ backgroundColor: MATH_COLOR }}
              />
              Math
            </span>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-2 sm:gap-4 text-center text-sm">
              <div>
                <div className="text-gray-500">Reading &amp; Writing</div>
                <div className="font-semibold" style={{ color: READING_COLOR }}>
                  {formatRange(latestSections.rw)}
                </div>
                {latestSections.rw.p50 != null && (
                  <div className="text-xs text-gray-500">Median {latestSections.rw.p50}</div>
                )}
              </div>
              <div>
                <div className="text-gray-500">Math</div>
                <div className="font-semibold" style={{ color: MATH_COLOR }}>
                  {formatRange(latestSections.math)}
                </div>
                {latestSections.math.p50 != null && (
                  <div className="text-xs text-gray-500">Median {latestSections.math.p50}</div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
