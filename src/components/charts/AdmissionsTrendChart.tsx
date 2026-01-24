"use client";

import { YearData } from "@/lib/types";
import { formatNumber } from "@/utils/dataHelpers";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface AdmissionsTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

export default function AdmissionsTrendChart({
  yearData,
  schoolColor,
}: AdmissionsTrendChartProps) {
  const years = Object.keys(yearData).sort();

  const trendData = years.map((year) => ({
    year: year.split("-")[0],
    fullYear: year,
    applications: yearData[year].admissions.applied,
    admitted: yearData[year].admissions.admitted,
    enrolled: yearData[year].admissions.enrolled,
    acceptanceRate: yearData[year].admissions.acceptanceRate * 100,
    yieldRate: yearData[year].admissions.yield * 100,
    edApplied: yearData[year].admissions.earlyDecision?.applied || 0,
    edAdmitted: yearData[year].admissions.earlyDecision?.admitted || 0,
  }));

  const hasEarlyDecision = trendData.some((d) => d.edApplied > 0);

  return (
    <div className="space-y-6">
      {/* Applications & Acceptance Rate Chart */}
      <div className="card p-6" style={{ backgroundColor: "#ffffff" }}>
        <h3 className="text-lg font-semibold mb-4 text-gray-800">
          Applications & Acceptance Rate Over Time
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis
                dataKey="year"
                tick={{ fontSize: 12, fill: "#666" }}
                axisLine={{ stroke: "#e5e5e5" }}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12, fill: "#666" }}
                axisLine={{ stroke: "#e5e5e5" }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                label={{
                  value: "Applications",
                  angle: -90,
                  position: "insideLeft",
                  style: { textAnchor: "middle", fill: "#666", fontSize: 12 },
                }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12, fill: "#666" }}
                axisLine={{ stroke: "#e5e5e5" }}
                tickFormatter={(v) => `${v}%`}
                domain={[0, 15]}
                label={{
                  value: "Acceptance Rate (%)",
                  angle: 90,
                  position: "insideRight",
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
                formatter={(value, name) => {
                  if (name === "acceptanceRate") {
                    return [`${(value as number).toFixed(1)}%`, "Acceptance Rate"];
                  }
                  return [formatNumber(value as number), name === "applications" ? "Applications" : name];
                }}
                labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
              />
              <Legend
                wrapperStyle={{ paddingTop: "10px" }}
                formatter={(value) => {
                  if (value === "applications") return "Applications";
                  if (value === "acceptanceRate") return "Acceptance Rate (%)";
                  return value;
                }}
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
      </div>

      {/* Early Decision Chart - if data exists */}
      {hasEarlyDecision && (
        <div className="card p-6" style={{ backgroundColor: "#ffffff" }}>
          <h3 className="text-lg font-semibold mb-4 text-gray-800">
            Early Decision Applications
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
        </div>
      )}

      {/* Complete Admissions Data Table */}
      <div className="card p-6" style={{ backgroundColor: "#ffffff" }}>
        <h3 className="text-lg font-semibold mb-4 text-gray-800">
          Complete Admissions Data
        </h3>
        <div className="overflow-x-auto">
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
              {trendData.slice().reverse().map((row) => (
                <tr key={row.fullYear}>
                  <td className="year-cell" style={{ color: schoolColor, textAlign: "left" }}>
                    {row.fullYear}
                  </td>
                  <td style={{ textAlign: "right" }}>{formatNumber(row.applications)}</td>
                  <td style={{ textAlign: "right" }}>{formatNumber(row.admitted)}</td>
                  <td style={{ textAlign: "right" }}>{formatNumber(row.enrolled)}</td>
                  <td style={{ textAlign: "right" }}>{row.acceptanceRate.toFixed(1)}%</td>
                  <td style={{ textAlign: "right" }}>{row.yieldRate.toFixed(1)}%</td>
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
