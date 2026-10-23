"use client";

import { useState } from "react";
import type { YearData } from "@/lib/types";
import { formatPercent } from "@/utils/dataHelpers";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface GenderAcceptanceChartProps {
  yearData: Record<string, YearData>;
}

const WOMEN_COLOR = "#eb6834";
const MEN_COLOR = "#2a78d6";

type Series = "women" | "men";

function rate(admitted: number | undefined, applied: number | undefined): number | null {
  if (typeof admitted !== "number" || typeof applied !== "number" || applied === 0) return null;
  return admitted / applied;
}

export default function GenderAcceptanceChart({ yearData }: GenderAcceptanceChartProps) {
  const [active, setActive] = useState<Series | null>(null);
  const isDimmed = (key: Series) => active !== null && active !== key;
  const trendData = Object.keys(yearData)
    .sort()
    .flatMap((year) => {
      const byGender = yearData[year].admissions.byGender;
      if (!byGender) return [];
      const women = rate(byGender.women.admitted, byGender.women.applied);
      const men = rate(byGender.men.admitted, byGender.men.applied);
      if (women == null || men == null) return [];
      return [{ year: year.split("-")[0], fullYear: year, women: women * 100, men: men * 100 }];
    });

  if (trendData.length === 0) return null;

  const latest = trendData[trendData.length - 1];
  const rateAxisMax = Math.max(
    5,
    Math.ceil((Math.max(...trendData.map((d) => Math.max(d.women, d.men))) + 1) / 5) * 5,
  );

  return (
    <div className="card p-4 sm:p-6" style={{ backgroundColor: "#ffffff" }}>
      <h3 className="text-lg font-semibold text-gray-800">Acceptance Rate by Gender</h3>
      <p className="text-sm text-gray-600 mt-1 mb-4">
        First-time, first-year applicants, Common Data Set Section C1.
      </p>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        {(
          [
            { key: "women", label: "Women", value: latest.women, color: WOMEN_COLOR },
            { key: "men", label: "Men", value: latest.men, color: MEN_COLOR },
          ] as const
        ).map(({ key, label, value, color }) => (
          <button
            type="button"
            key={key}
            onMouseEnter={() => setActive(key)}
            onMouseLeave={() => setActive(null)}
            onFocus={() => setActive(key)}
            onBlur={() => setActive(null)}
            className="flex items-center gap-2 rounded-full px-3 py-2 text-xs font-medium transition-colors cursor-default"
            style={{
              border: `1px solid ${active === key ? "rgba(0,0,0,0.22)" : "rgba(0,0,0,0.1)"}`,
              color: isDimmed(key) ? "#9096a0" : "#1a1a1a",
              background: active === key ? "rgba(0,0,0,0.04)" : "transparent",
            }}
          >
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ background: color, opacity: isDimmed(key) ? 0.35 : 1 }}
              aria-hidden
            />
            {label}
            <span style={{ color: "#62666d" }} className="tabular-nums">
              {formatPercent(value / 100)}
            </span>
          </button>
        ))}
        <span className="text-xs text-gray-400">{latest.fullYear}</span>
      </div>

      <div className="h-72 sm:h-80">
        <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height="100%">
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis
              dataKey="year"
              tick={{ fontSize: 12, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
            />
            <YAxis
              width={36}
              tick={{ fontSize: 10, fill: "#666" }}
              axisLine={{ stroke: "#e5e5e5" }}
              tickFormatter={(v) => `${Math.round(v)}%`}
              domain={[0, rateAxisMax]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e5e5",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              }}
              formatter={(value, name) => [
                `${(value as number).toFixed(1)}%`,
                name === "women" ? "Women" : "Men",
              ]}
              labelFormatter={(label) => `${label}-${parseInt(label as string, 10) + 1}`}
            />
            <Line
              type="monotone"
              dataKey="women"
              stroke={WOMEN_COLOR}
              strokeWidth={3}
              strokeOpacity={isDimmed("women") ? 0.2 : 1}
              dot={{
                fill: WOMEN_COLOR,
                strokeWidth: 2,
                r: 5,
                opacity: isDimmed("women") ? 0.2 : 1,
              }}
              activeDot={{ r: 7 }}
            />
            <Line
              type="monotone"
              dataKey="men"
              stroke={MEN_COLOR}
              strokeWidth={3}
              strokeOpacity={isDimmed("men") ? 0.2 : 1}
              dot={{ fill: MEN_COLOR, strokeWidth: 2, r: 5, opacity: isDimmed("men") ? 0.2 : 1 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
