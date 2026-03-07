"use client";

import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  LabelList,
} from "recharts";

function useIsMobile(breakpoint = 640) {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < breakpoint);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, [breakpoint]);
  return isMobile;
}
import {
  platformStats,
  demographicGrowth,
  internationalByRegion,
  countryDeclines,
  countryGains,
  scoreReportingGrowth,
  testRequirementHistory,
  lowerScoreSubmissionGroups,
  selectivityGrowth,
  lede,
  takeaways,
} from "@/data/trends/common-app-2026/data";

const ACCENT = "#1D4F91";
const POSITIVE = "#16A34A"; // green-600
const NEGATIVE = "#DC2626"; // red-600
const NEUTRAL = "#6B7280"; // gray-500
const LIGHT_GRAY = "#F3F4F6"; // gray-100

function fmtPct(v: unknown): string {
  if (typeof v !== "number") return "";
  return `${v > 0 ? "+" : ""}${v}%`;
}

// ─── Section 1: Platform Stat Cards ──────────────────────────────────────────

function PlatformStats() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {platformStats.map((s) => (
        <div key={s.label} className="card p-5 text-center">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
            {s.label}
          </p>
          <p className="text-3xl font-bold text-gray-900 mb-1">{s.value2026}</p>
          <p
            className="text-sm font-semibold"
            style={{ color: s.changePct > 0 ? POSITIVE : NEGATIVE }}
          >
            {s.changePct > 0 ? "+" : ""}
            {s.changePct}% vs 2024-25
          </p>
          <p className="text-xs text-gray-400 mt-1">{s.note}</p>
        </div>
      ))}
    </div>
  );
}

// ─── Section 2: Demographic Growth Bar Chart ─────────────────────────────────

function DemographicGrowthChart() {
  const sorted = [...demographicGrowth].sort((a, b) => b.growth - a.growth);
  const isMobile = useIsMobile();

  const yAxisWidth = isMobile ? 116 : 164;
  const leftMargin = isMobile ? 0 : 168;
  const rightMargin = isMobile ? 36 : 56;
  const labelFontSize = isMobile ? 10 : 11;
  const tickFontSize = isMobile ? 10 : 12;

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Application Growth by Group, 2024-25 → 2025-26
      </h3>
      <p className="text-sm text-gray-500 mb-5">
        % change in applicants vs the same point in the prior season
      </p>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart
          layout="vertical"
          data={sorted}
          margin={{ top: 4, right: rightMargin, left: leftMargin, bottom: 4 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#f0f0f0"
            horizontal={false}
          />
          <XAxis
            type="number"
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: tickFontSize }}
            domain={[-2, 12]}
          />
          <YAxis
            type="category"
            dataKey="group"
            tick={{ fontSize: tickFontSize }}
            width={yAxisWidth}
          />
          <Tooltip formatter={fmtPct} cursor={{ fill: LIGHT_GRAY }} />
          <ReferenceLine x={0} stroke="#9CA3AF" />
          <Bar dataKey="growth" radius={[0, 3, 3, 0]} name="Growth">
            <LabelList
              dataKey="growth"
              position="right"
              formatter={fmtPct}
              style={{ fontSize: labelFontSize, fontWeight: 600, fill: "#374151" }}
            />
            {sorted.map((entry) => (
              <Cell
                key={entry.group}
                fill={
                  entry.group === "All Applicants"
                    ? NEUTRAL
                    : entry.growth >= 5
                    ? ACCENT
                    : entry.growth >= 2
                    ? "#60A5FA"
                    : "#D1D5DB"
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2">
        Source: Common App Deadline Update, 2025-2026, through February 1. URM = underrepresented minority (Black/AA, Latinx, American Indian/AK Native, Native Hawaiian/Pacific Islander).
      </p>
    </div>
  );
}

// ─── Section 3a: International by Region ────────────────────────────────────

function InternationalRegionChart() {
  const data = [...internationalByRegion].sort((a, b) => b.growth - a.growth);

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        International Applicants by Region
      </h3>
      <p className="text-sm text-gray-500 mb-5">
        % change vs same point in 2024-25 season
      </p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          data={data}
          margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="region" tick={{ fontSize: 12 }} />
          <YAxis
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            domain={[-20, 8]}
          />
          <Tooltip formatter={fmtPct} cursor={{ fill: LIGHT_GRAY }} />
          <ReferenceLine y={0} stroke="#9CA3AF" />
          <Bar dataKey="growth" radius={[3, 3, 0, 0]} name="Growth">
            <LabelList
              dataKey="growth"
              position="top"
              formatter={fmtPct}
              style={{ fontSize: 11, fontWeight: 600, fill: "#374151" }}
            />
            {data.map((entry) => (
              <Cell
                key={entry.region}
                fill={entry.growth >= 0 ? POSITIVE : NEGATIVE}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2">
        Source: Common App Deadline Update, 2025-2026, through February 1.
      </p>
    </div>
  );
}

// ─── Section 3b: Country-Level Changes ──────────────────────────────────────

function CountryChangesChart() {
  // Show declines and gains in one horizontal bar chart
  const data = [
    ...countryGains.map((c) => ({ ...c, type: "gain" as const })),
    ...countryDeclines
      .sort((a, b) => a.growth - b.growth)
      .map((c) => ({ ...c, type: "decline" as const })),
  ];

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Country-Level Standouts
      </h3>
      <p className="text-sm text-gray-500 mb-5">
        % change in applicants vs 2024-25 — top gains and notable declines
      </p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 4, right: 64, left: 80, bottom: 4 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#f0f0f0"
            horizontal={false}
          />
          <XAxis
            type="number"
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            domain={[-50, 150]}
          />
          <YAxis
            type="category"
            dataKey="country"
            tick={{ fontSize: 12 }}
            width={76}
          />
          <Tooltip formatter={fmtPct} cursor={{ fill: LIGHT_GRAY }} />
          <ReferenceLine x={0} stroke="#9CA3AF" />
          <Bar dataKey="growth" radius={[0, 3, 3, 0]} name="Growth">
            <LabelList
              dataKey="growth"
              content={(props: Record<string, unknown>) => {
                const x = props.x as number;
                const y = props.y as number;
                const width = props.width as number;
                const height = props.height as number;
                const value = props.value as number;
                return (
                  <text
                    x={x + Math.max(width, 0) + 4}
                    y={y + height / 2}
                    textAnchor="start"
                    dominantBaseline="middle"
                    fontSize={11}
                    fontWeight={600}
                    fill="#374151"
                  >
                    {fmtPct(value)}
                  </text>
                );
              }}
            />
            {data.map((entry) => (
              <Cell
                key={entry.country}
                fill={entry.growth >= 0 ? POSITIVE : NEGATIVE}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2">
        Source: Common App Deadline Update, 2025-2026, through February 1.
      </p>
    </div>
  );
}

// ─── Section 4: Test Score Reporting ────────────────────────────────────────

function ScoreReportingChart() {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Score Reporters vs Non-Reporters
      </h3>
      <p className="text-sm text-gray-500 mb-5">
        % change in applicants by test score reporting behavior, 2024-25 → 2025-26
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart
          data={scoreReportingGrowth}
          margin={{ top: 4, right: 60, left: 16, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="group" tick={{ fontSize: 13 }} />
          <YAxis
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            domain={[-10, 15]}
          />
          <Tooltip formatter={fmtPct} cursor={{ fill: LIGHT_GRAY }} />
          <ReferenceLine y={0} stroke="#9CA3AF" />
          <Bar dataKey="growth" radius={[3, 3, 0, 0]} name="Growth">
            <LabelList
              dataKey="growth"
              position="top"
              formatter={fmtPct}
              style={{ fontSize: 12, fontWeight: 700, fill: "#374151" }}
            />
            {scoreReportingGrowth.map((entry) => (
              <Cell
                key={entry.group}
                fill={entry.growth >= 0 ? ACCENT : NEGATIVE}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function TestRequirementChart() {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        % of Common App Members Requiring Test Scores
      </h3>
      <p className="text-sm text-gray-500 mb-5">
        The test-optional wave — from majority to near-zero in five years
      </p>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart
          data={testRequirementHistory}
          margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="season" tick={{ fontSize: 12 }} />
          <YAxis
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            domain={[0, 65]}
          />
          <Tooltip formatter={(v) => [`${v}%`, "Members requiring scores"]} />
          <Bar
            dataKey="pctRequiring"
            fill={ACCENT}
            radius={[3, 3, 0, 0]}
            name="% Requiring"
          >
            <LabelList
              dataKey="pctRequiring"
              position="top"
              formatter={(v: unknown) => typeof v === "number" ? `${v}%` : ""}
              style={{ fontSize: 11, fontWeight: 600, fill: "#374151" }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2">
        Only 2019-20 and 2023-24 through 2025-26 are explicitly reported in the source document.
        Source: Common App Deadline Update, 2025-2026; Common App research reports.
      </p>
    </div>
  );
}

// ─── Section 5: Selectivity Band Chart ───────────────────────────────────────

function SelectivityChart() {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Application Growth by Institutional Selectivity
      </h3>
      <p className="text-sm text-gray-500 mb-5">
        % change in applications by member admit rate band, 2024-25 → 2025-26
      </p>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart
          data={selectivityGrowth}
          margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="band"
            tick={{ fontSize: 12 }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
            domain={[0, 10]}
          />
          <Tooltip
            formatter={(v) => [`+${v}%`, "Application growth"]}
            labelFormatter={(label, payload) => {
              const row = payload?.[0]?.payload;
              return `${label} (${row?.admitRange ?? ""})`;
            }}
          />
          <Bar dataKey="growth" radius={[3, 3, 0, 0]} name="Growth">
            <LabelList
              dataKey="growth"
              position="top"
              formatter={(v: unknown) => typeof v === "number" ? `+${v}%` : ""}
              style={{ fontSize: 12, fontWeight: 700, fill: "#374151" }}
            />
            {selectivityGrowth.map((entry) => (
              <Cell
                key={entry.band}
                fill={entry.band === "Most Selective" ? "#9CA3AF" : ACCENT}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2">
        "Most Selective" = member admit rates below 25%, which includes all schools tracked on this site.
        Source: Common App Deadline Update, 2025-2026, through February 1.
      </p>
    </div>
  );
}

// ─── Main Export ─────────────────────────────────────────────────────────────

export default function CommonApp2026Story() {
  return (
    <div className="space-y-8">
      {/* Lede */}
      <div className="card p-6">
        <p className="text-gray-700 leading-relaxed text-base">{lede}</p>
      </div>

      {/* Fault Line 1: The Surge */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-1">
          1 — The Record Numbers
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Application volume hit a new high, and students are casting wider nets.
        </p>
        <PlatformStats />
      </div>

      {/* Fault Line 2: Growing Apart */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-1">
          2 — Growing Apart
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Not all students are applying at the same rate. Low-income, first-generation,
          and underrepresented applicants are outpacing their peers by a wide margin —
          while continuing-generation and higher-income applicants are essentially flat.
        </p>
        <DemographicGrowthChart />
      </div>

      {/* Fault Line 3: The International Cliff */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-1">
          3 — The International Cliff
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          International applicants fell 9% from last season — a sharp reversal after years
          of growth. Asia and Africa drove the decline, while the Americas bucked the trend.
          The drops in individual countries are even more striking.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InternationalRegionChart />
          <CountryChangesChart />
        </div>
      </div>

      {/* Fault Line 4: Test Scores Come Back */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-1">
          4 — Test Scores Come Back
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          After the COVID-era collapse — when the share of schools requiring scores fell
          from 55% to just 4% — score submission is rebounding sharply. Reporters are up
          11%; non-reporters are down 5%; reporters now outnumber non-reporters early in
          the season for the first time in years. The equity gap remains: first-gen, URM,
          and low-income students are still less likely to submit a score.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ScoreReportingChart />
          <TestRequirementChart />
        </div>
        <div className="card p-5 mt-6">
          <p className="text-sm font-semibold text-gray-700 mb-2">
            Groups less likely to submit a test score:
          </p>
          <ul className="space-y-1">
            {lowerScoreSubmissionGroups.map((g) => (
              <li key={g} className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 rounded-full bg-gray-400 flex-shrink-0" />
                {g}
              </li>
            ))}
          </ul>
          <p className="text-xs text-gray-400 mt-3">
            All groups saw score reporters grow faster than non-reporters — but the gap
            persists. Source: Common App Deadline Update, 2025-2026.
          </p>
        </div>
      </div>

      {/* Fault Line 5: Selective Schools Grow Slowest */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-1">
          5 — The Most Selective Schools Grow Slowest
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Every selectivity tier grew — but the most selective schools (admit rates below 25%,
          which includes every school on this site) saw only +3% application growth, less than
          half the rate of every other tier. The decline in international applicants likely plays
          a role: international students disproportionately target elite institutions, and they
          fell 19% at the most selective schools specifically.
        </p>
        <SelectivityChart />
      </div>

      {/* Key Takeaways */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Key Takeaways
        </h3>
        <ul className="space-y-2">
          {takeaways.map((t, i) => (
            <li
              key={i}
              className="flex items-start gap-3 text-gray-700 text-sm"
            >
              <span className="mt-1.5 w-2 h-2 rounded-full bg-gray-800 flex-shrink-0" />
              {t}
            </li>
          ))}
        </ul>
        <p className="text-xs text-gray-400 mt-4">
          Source: Common App &ldquo;Deadline Update, 2025-2026: First-year application trends through
          February 1,&rdquo; published February 12, 2026. Data reflects 913 returning member institutions.
        </p>
      </div>
    </div>
  );
}
