"use client";

import { useState } from "react";
import { YearData } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface AdmissionsTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

export default function AdmissionsTrendChart({
  yearData,
  schoolColor,
}: AdmissionsTrendChartProps) {
  const [showAllMobileRows, setShowAllMobileRows] = useState(false);
  const years = Object.keys(yearData).sort();

  const trendData = years.map((year) => {
    const admissions = yearData[year].admissions;
    return {
      year: year.split("-")[0],
      fullYear: year,
      applications: admissions.applied,
      admitted: admissions.admitted,
      enrolled: admissions.enrolled,
      acceptanceRate:
        typeof admissions.acceptanceRate === "number"
          ? admissions.acceptanceRate * 100
          : null,
      yieldRate: typeof admissions.yield === "number" ? admissions.yield * 100 : null,
      edApplied: admissions.earlyDecision?.applied ?? 0,
      edAdmitted: admissions.earlyDecision?.admitted ?? 0,
    };
  });

  const hasEarlyDecision = trendData.some((d) => d.edApplied > 0);
  const acceptanceRateAxisMax = Math.max(
    15,
    Math.ceil(
      (Math.max(...trendData.map((d) => d.acceptanceRate ?? 0)) + 5) / 10
    ) * 10
  );
  const newestFirst = trendData.slice().reverse();

  return (
    <div className="space-y-6">
      {/* Applications & Acceptance Rate Chart */}
      <div className="card p-4 sm:p-6" style={{ backgroundColor: "#ffffff" }}>
        <h3 className="text-lg font-semibold mb-4 text-gray-800">
          Applications & Acceptance Rate Over Time
        </h3>
        <div className="h-72 sm:h-80">
          <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height="100%">
            <ComposedChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis
                dataKey="year"
                tick={{ fontSize: 12, fill: "#666" }}
                axisLine={{ stroke: "#e5e5e5" }}
              />
              <YAxis
                yAxisId="left"
                width={38}
                tick={{ fontSize: 10, fill: "#666" }}
                axisLine={{ stroke: "#e5e5e5" }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                width={36}
                tick={{ fontSize: 10, fill: "#666" }}
                axisLine={{ stroke: "#e5e5e5" }}
                tickFormatter={(v) => `${Math.round(v)}%`}
                domain={[0, acceptanceRateAxisMax]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e5e5e5",
                  borderRadius: "8px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                }}
                formatter={(value, name) => {
                  if (name === "acceptanceRate") {
                    return [`${(value as number).toFixed(1)}%`, "Acceptance Rate"];
                  }
                  return [formatNumber(value as number), name === "applications" ? "Applications" : name];
                }}
                labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
              />
              <Bar
                yAxisId="left"
                dataKey="applications"
                fill={schoolColor}
                fillOpacity={0.7}
                radius={[4, 4, 0, 0]}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="acceptanceRate"
                stroke="#e67e22"
                strokeWidth={3}
                dot={{ fill: "#e67e22", strokeWidth: 2, r: 5 }}
                activeDot={{ r: 7 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs text-gray-600">
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: schoolColor }} />Applications</span>
          <span className="flex items-center gap-1.5"><span className="h-0.5 w-4 bg-orange-500" />Acceptance Rate</span>
        </div>
      </div>

      {/* Early Decision Chart - if data exists */}
      {hasEarlyDecision && (
        <div className="card p-4 sm:p-6" style={{ backgroundColor: "#ffffff" }}>
          <h3 className="text-lg font-semibold mb-4 text-gray-800">
            Early Decision Applications
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
                <Bar
                  dataKey="edApplied"
                  name="ED Applications"
                  fill={schoolColor}
                  fillOpacity={0.5}
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="edAdmitted"
                  name="ED Admits"
                  fill="#27ae60"
                  radius={[4, 4, 0, 0]}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs text-gray-600">
            <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm opacity-60" style={{ backgroundColor: schoolColor }} />ED Applications</span>
            <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-green-600" />ED Admits</span>
          </div>
        </div>
      )}

      {/* Complete Admissions Data Table */}
      <div className="card p-4 sm:p-6" style={{ backgroundColor: "#ffffff" }}>
        <h3 className="text-lg font-semibold mb-4 text-gray-800">
          Complete Admissions Data
        </h3>
        <div className="md:hidden divide-y divide-gray-100 border-y border-gray-100">
          {(showAllMobileRows ? newestFirst : newestFirst.slice(0, 4)).map((row) => (
            <article key={`mobile-${row.fullYear}`} className="py-4 first:pt-2">
              <div className="flex items-start justify-between gap-3 mb-3">
                <h4 className="font-semibold" style={{ color: schoolColor }}>{row.fullYear}</h4>
                <div className="text-right">
                  <div className="text-xs uppercase tracking-wide text-gray-400">Accept rate</div>
                  <div className="text-lg font-bold" style={{ color: schoolColor }}>
                    {formatPercent(row.acceptanceRate == null ? undefined : row.acceptanceRate / 100)}
                  </div>
                </div>
              </div>
              <dl className="grid grid-cols-3 gap-2 text-sm">
                {[
                  ["Applicants", formatNumber(row.applications)],
                  ["Admits", formatNumber(row.admitted)],
                  ["Enrolled", formatNumber(row.enrolled)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <dt className="text-xs uppercase tracking-wide text-gray-400">{label}</dt>
                    <dd className="font-medium text-gray-700 mt-0.5">{value}</dd>
                  </div>
                ))}
              </dl>
              <dl className={`grid ${hasEarlyDecision ? "grid-cols-3" : "grid-cols-1"} gap-2 text-sm mt-3 pt-3 border-t border-gray-100`}>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-400">Yield</dt>
                  <dd className="font-medium text-gray-700 mt-0.5">
                    {formatPercent(row.yieldRate == null ? undefined : row.yieldRate / 100)}
                  </dd>
                </div>
                {hasEarlyDecision && (
                  <>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-gray-400">ED Apps</dt>
                      <dd className="font-medium text-gray-700 mt-0.5">{row.edApplied > 0 ? formatNumber(row.edApplied) : "—"}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-gray-400">ED Admits</dt>
                      <dd className="font-medium text-gray-700 mt-0.5">{row.edAdmitted > 0 ? formatNumber(row.edAdmitted) : "—"}</dd>
                    </div>
                  </>
                )}
              </dl>
            </article>
          ))}
          {newestFirst.length > 4 && (
            <button
              type="button"
              onClick={() => setShowAllMobileRows((show) => !show)}
              className="w-full min-h-11 mt-2 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50"
            >
              {showAllMobileRows ? "Show recent years" : `Show all ${newestFirst.length} years`}
            </button>
          )}
        </div>

        <div className="hidden md:block overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>Year</th>
                <th style={{ textAlign: "right" }}>Applications</th>
                <th style={{ textAlign: "right" }}>Admits</th>
                <th style={{ textAlign: "right" }}>Enrolled</th>
                <th style={{ textAlign: "right" }}>Accept Rate</th>
                <th style={{ textAlign: "right" }}>Yield Rate</th>
                {hasEarlyDecision && (
                  <>
                    <th style={{ textAlign: "right" }}>ED Apps</th>
                    <th style={{ textAlign: "right" }}>ED Admits</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {newestFirst.map((row) => (
                <tr key={row.fullYear}>
                  <td className="year-cell" style={{ color: schoolColor, textAlign: "left" }}>
                    {row.fullYear}
                  </td>
                  <td style={{ textAlign: "right" }}>{formatNumber(row.applications)}</td>
                  <td style={{ textAlign: "right" }}>{formatNumber(row.admitted)}</td>
                  <td style={{ textAlign: "right" }}>{formatNumber(row.enrolled)}</td>
                  <td style={{ textAlign: "right" }}>{formatPercent(
                    row.acceptanceRate == null ? undefined : row.acceptanceRate / 100
                  )}</td>
                  <td style={{ textAlign: "right" }}>{formatPercent(
                    row.yieldRate == null ? undefined : row.yieldRate / 100
                  )}</td>
                  {hasEarlyDecision && (
                    <>
                      <td style={{ textAlign: "right" }}>{row.edApplied > 0 ? formatNumber(row.edApplied) : "-"}</td>
                      <td style={{ textAlign: "right" }}>{row.edAdmitted > 0 ? formatNumber(row.edAdmitted) : "-"}</td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
