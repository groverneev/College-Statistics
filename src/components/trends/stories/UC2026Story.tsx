"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";
import {
  campusData,
  appTypeMix,
  lede,
  takeaways,
} from "@/data/trends/uc-2026-applications/data";

const BLUE_2025 = "#6B7280"; // gray-500
const BLUE_2026 = "#1D4F91"; // deep blue

function formatK(val: number | string | undefined) {
  if (typeof val !== "number") return "";
  return `${(val / 1000).toFixed(0)}k`;
}

function fmtNum(val: number | string | undefined) {
  if (typeof val !== "number") return "";
  return val.toLocaleString();
}

function fmtPct(val: number | string | undefined) {
  if (typeof val !== "number") return "";
  return `${val}%`;
}

// Chart 1: First-Year Applications by Campus (grouped bar)
function FirstYearByCampus() {
  const data = campusData.map((d) => ({
    campus: d.campus,
    "Fall 2025": d.firstYear2025,
    "Fall 2026": d.firstYear2026,
  }));

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        First-Year Applications by Campus
      </h3>
      <p className="text-sm text-gray-500 mb-4">Fall 2025 vs Fall 2026</p>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="campus" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={formatK} tick={{ fontSize: 12 }} />
          <Tooltip formatter={fmtNum} />
          <Legend />
          <Bar dataKey="Fall 2025" fill={BLUE_2025} radius={[2, 2, 0, 0]} />
          <Bar dataKey="Fall 2026" fill={BLUE_2026} radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Chart 2: YoY % Change by Campus (first-year, horizontal bar)
function YoYChange() {
  const data = campusData
    .map((d) => ({
      campus: d.campus,
      change: parseFloat(
        (((d.firstYear2026 - d.firstYear2025) / d.firstYear2025) * 100).toFixed(
          1
        )
      ),
    }))
    .sort((a, b) => b.change - a.change);

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        First-Year Application Growth by Campus
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        Year-over-year % change, Fall 2025 → Fall 2026
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 4, right: 40, left: 60, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
          <XAxis
            type="number"
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            domain={["dataMin - 1", "dataMax + 1"]}
          />
          <YAxis type="category" dataKey="campus" tick={{ fontSize: 12 }} width={80} />
          <Tooltip formatter={fmtPct} />
          <ReferenceLine x={0} stroke="#9CA3AF" />
          <Bar dataKey="change" radius={[0, 2, 2, 0]} name="YoY Change">
            {data.map((entry) => (
              <Cell
                key={entry.campus}
                fill={entry.change >= 0 ? BLUE_2026 : "#EF4444"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Chart 3: Application type mix system-wide (stacked bar)
function AppTypeMix() {
  const data = appTypeMix.map((d) => ({
    year: d.year,
    "CA Resident": d.caResident,
    "Domestic Out-of-State": d.domesticOOS,
    International: d.international,
  }));

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        First-Year Application Mix (System-Wide)
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        CA Resident vs Domestic OOS vs International
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 13 }} />
          <YAxis tickFormatter={formatK} tick={{ fontSize: 12 }} />
          <Tooltip formatter={fmtNum} />
          <Legend />
          <Bar
            dataKey="CA Resident"
            stackId="a"
            fill="#1D4F91"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="Domestic Out-of-State"
            stackId="a"
            fill="#6B7280"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="International"
            stackId="a"
            fill="#9CA3AF"
            radius={[2, 2, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Chart 4: Transfer Applications by Campus (grouped bar)
function TransferByCampus() {
  const data = campusData.map((d) => ({
    campus: d.campus,
    "Fall 2025": d.transfer2025,
    "Fall 2026": d.transfer2026,
  }));

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Transfer Applications by Campus
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        Fall 2025 vs Fall 2026 — Merced nearly doubled
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="campus" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={formatK} tick={{ fontSize: 12 }} />
          <Tooltip formatter={fmtNum} />
          <Legend />
          <Bar dataKey="Fall 2025" fill={BLUE_2025} radius={[2, 2, 0, 0]} />
          <Bar dataKey="Fall 2026" fill={BLUE_2026} radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Full data table
function DataTable() {
  return (
    <div className="card p-6 overflow-x-auto">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Full Data: First-Year &amp; Transfer Applications
      </h3>
      <table className="w-full text-sm text-left">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="py-2 pr-4 text-gray-500 font-medium">Campus</th>
            <th className="py-2 px-3 text-gray-500 font-medium text-right">FY 2025</th>
            <th className="py-2 px-3 text-gray-500 font-medium text-right">FY 2026</th>
            <th className="py-2 px-3 text-gray-500 font-medium text-right">FY Δ%</th>
            <th className="py-2 px-3 text-gray-500 font-medium text-right">Tr 2025</th>
            <th className="py-2 px-3 text-gray-500 font-medium text-right">Tr 2026</th>
            <th className="py-2 pl-3 text-gray-500 font-medium text-right">Tr Δ%</th>
          </tr>
        </thead>
        <tbody>
          {campusData.map((d) => {
            const fyChange = (((d.firstYear2026 - d.firstYear2025) / d.firstYear2025) * 100).toFixed(1);
            const trChange = (((d.transfer2026 - d.transfer2025) / d.transfer2025) * 100).toFixed(1);
            const fyPos = parseFloat(fyChange) >= 0;
            const trPos = parseFloat(trChange) >= 0;
            return (
              <tr key={d.campus} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-2 pr-4 font-medium text-gray-800">{d.campus}</td>
                <td className="py-2 px-3 text-right text-gray-600">{d.firstYear2025.toLocaleString()}</td>
                <td className="py-2 px-3 text-right text-gray-800 font-medium">{d.firstYear2026.toLocaleString()}</td>
                <td className={`py-2 px-3 text-right font-medium ${fyPos ? "text-blue-700" : "text-red-600"}`}>
                  {fyPos ? "+" : ""}{fyChange}%
                </td>
                <td className="py-2 px-3 text-right text-gray-600">{d.transfer2025.toLocaleString()}</td>
                <td className="py-2 px-3 text-right text-gray-800 font-medium">{d.transfer2026.toLocaleString()}</td>
                <td className={`py-2 pl-3 text-right font-medium ${trPos ? "text-blue-700" : "text-red-600"}`}>
                  {trPos ? "+" : ""}{trChange}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="text-xs text-gray-400 mt-3">
        FY = First-Year applications. Tr = Transfer applications. Source: UC Office of the President, Preliminary Application Summary Counts (Fall 2025, Fall 2026).
      </p>
    </div>
  );
}

export default function UC2026Story() {
  return (
    <div className="space-y-8">
      {/* Lede */}
      <div className="card p-6">
        <p className="text-gray-700 leading-relaxed text-base">{lede}</p>
      </div>

      {/* Charts */}
      <FirstYearByCampus />
      <YoYChange />
      <AppTypeMix />
      <TransferByCampus />

      {/* Key Takeaways */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Key Takeaways</h3>
        <ul className="space-y-2">
          {takeaways.map((t, i) => (
            <li key={i} className="flex items-start gap-3 text-gray-700 text-sm">
              <span className="mt-1 w-2 h-2 rounded-full bg-gray-800 flex-shrink-0" />
              {t}
            </li>
          ))}
        </ul>
      </div>

      {/* Data Table */}
      <DataTable />
    </div>
  );
}
