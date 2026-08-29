"use client";

import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import {
  apCsaSeries,
  csSplitSeries,
  sciIndexedSeries,
  declinesBySource,
  lede,
  sections,
  takeaways,
  sourceLinks,
  sourceNote,
} from "@/data/trends/cs-enrollment-reversal/data";

const RED = "#b3322a"; // CS A / declines
const BLUE = "#3468b8"; // CS Principles / Chemistry
const GREEN = "#2f7d4f"; // Biology
const AMBER = "#a06b0e"; // Physics 1
const GRAY = "#6B7280"; // pre-peak growth era

function formatK(val: number | string | undefined) {
  if (typeof val !== "number") return "";
  return `${(val / 1000).toFixed(0)}k`;
}

function fmtNum(val: number | string | undefined) {
  if (typeof val !== "number") return "";
  return val.toLocaleString();
}

function MobileDeclinesList({
  rows,
}: {
  rows: { source: string; window: string; change: number }[];
}) {
  const maxMagnitude = Math.max(...rows.map((row) => Math.abs(row.change)));

  return (
    <div className="space-y-4 sm:hidden">
      {rows.map((row) => (
        <div key={`${row.source}-${row.window}`}>
          <div className="mb-1 flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="text-sm font-medium text-gray-700">{row.source}</div>
              <div className="text-xs text-gray-400">{row.window}</div>
            </div>
            <span className="shrink-0 text-sm font-semibold tabular-nums text-red-600">
              {row.change}%
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full"
              style={{ width: `${(Math.abs(row.change) / maxMagnitude) * 100}%`, backgroundColor: RED }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// Prose section card, optionally with bullets and a closing line
function Section({
  heading,
  body,
  bullets,
  coda,
}: {
  heading: string;
  body?: string;
  bullets?: string[];
  coda?: string;
}) {
  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">{heading}</h3>
      {body && <p className="text-gray-700 leading-relaxed text-sm">{body}</p>}
      {bullets && (
        <ul className="space-y-2 mt-3">
          {bullets.map((b, i) => (
            <li key={i} className="flex items-start gap-3 text-gray-700 text-sm">
              <span className="mt-1.5 w-2 h-2 rounded-full bg-gray-800 flex-shrink-0" />
              {b}
            </li>
          ))}
        </ul>
      )}
      {coda && (
        <p className="text-gray-700 leading-relaxed text-sm mt-3">{coda}</p>
      )}
    </div>
  );
}

// Chart 1: AP CS A test takers, 2002–2026 (growth era gray, decline red)
function ApCsaChart() {
  const data = apCsaSeries.map((d) => ({
    year: d.year,
    "Test takers": d.year <= 2024 ? d.testTakers : null,
    Decline: d.year >= 2024 ? d.testTakers : null,
  }));

  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        AP Computer Science A Test Takers
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        2002–2026 · 2026 preliminary · decline from the 2024 peak in red
      </p>
      <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={320}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} minTickGap={24} />
          <YAxis tickFormatter={formatK} tick={{ fontSize: 12 }} />
          <Tooltip formatter={fmtNum} />
          <Line
            dataKey="Test takers"
            stroke={GRAY}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            dataKey="Decline"
            stroke={RED}
            strokeWidth={2.5}
            dot={{ r: 3, fill: RED }}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-3">
        The 2026 count (~81,500) is down about 17% from the 2024 peak of 98,136,
        returning the exam to its 2022–2023 range. Source: College Board.
      </p>
    </div>
  );
}

// Chart 2: AP science exams indexed to 2024 (2024 = 100)
function SciIndexedChart() {
  const data = sciIndexedSeries.map((d) => ({
    year: d.year,
    "AP Biology": d.biologyIdx,
    "AP Chemistry": d.chemistryIdx,
    "AP Physics 1": d.physics1Idx,
    "AP CS A": d.csaIdx,
  }));

  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        AP Science Exams Indexed to 2024
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        2024 = 100 · each exam indexed to its own 2024 total · 2026 preliminary
      </p>
      <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={300}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 13 }} />
          <YAxis domain={[78, 126]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <ReferenceLine y={100} stroke="#9CA3AF" strokeDasharray="4 4" />
          <Line
            dataKey="AP Biology"
            stroke={GREEN}
            strokeWidth={2}
            dot={{ r: 3, fill: GREEN }}
            activeDot={{ r: 4 }}
          />
          <Line
            dataKey="AP Chemistry"
            stroke={BLUE}
            strokeWidth={2}
            dot={{ r: 3, fill: BLUE }}
            activeDot={{ r: 4 }}
          />
          <Line
            dataKey="AP Physics 1"
            stroke={AMBER}
            strokeWidth={2}
            dot={{ r: 3, fill: AMBER }}
            activeDot={{ r: 4 }}
          />
          <Line
            dataKey="AP CS A"
            stroke={RED}
            strokeWidth={3}
            dot={{ r: 3, fill: RED }}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-3">
        By 2026, Biology and Chemistry are up about 22% and Physics 1 about 12%,
        while CS A is down about 17%. Source: College Board.
      </p>
    </div>
  );
}

// Chart 3: AP CS A vs CS Principles, 2022–2026
function CsSplitChart() {
  const data = csSplitSeries.map((d) => ({
    year: d.year,
    "AP CS Principles": d.csp,
    "AP CS A": d.csa,
  }));

  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        AP CS A vs. CS Principles Test Takers
      </h3>
      <p className="text-sm text-gray-500 mb-4">2022–2026 · 2026 preliminary</p>
      <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={300}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 13 }} />
          <YAxis
            domain={[0, 190000]}
            tickFormatter={formatK}
            tick={{ fontSize: 12 }}
          />
          <Tooltip formatter={fmtNum} />
          <Legend />
          <Line
            dataKey="AP CS Principles"
            stroke={BLUE}
            strokeWidth={2}
            dot={{ r: 3, fill: BLUE }}
            activeDot={{ r: 4 }}
          />
          <Line
            dataKey="AP CS A"
            stroke={RED}
            strokeWidth={2}
            dot={{ r: 3, fill: RED }}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-3">
        Both peaked in 2024. CS Principles held roughly flat through 2025 before
        dipping; CS A fell in both 2025 and 2026, about 2.5x faster off the peak.
        Source: College Board.
      </p>
    </div>
  );
}

// Chart 4: declines by source (horizontal bar, windows differ)
function DeclinesBySourceChart() {
  const data = declinesBySource.map((d) => ({
    source: `${d.source} (${d.window})`,
    change: d.change,
  }));

  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        CS Enrollment Declines by Source
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        Percent change · measurement window noted per bar
      </p>
      <MobileDeclinesList rows={declinesBySource} />
      <div className="hidden sm:block">
        <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={300}>
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 4, right: 40, left: 100, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
            <XAxis
              type="number"
              domain={[-20, 0]}
              tickFormatter={(v) => `${v}%`}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              type="category"
              dataKey="source"
              tick={{ fontSize: 11 }}
              width={140}
            />
            <Tooltip formatter={(v) => `${v}%`} />
            <ReferenceLine x={0} stroke="#9CA3AF" />
            <Bar
              dataKey="change"
              fill={RED}
              radius={[0, 2, 2, 0]}
              name="Change"
              barSize={28}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-gray-400 mt-3">
        Windows differ: AP is a two-year change from the 2024 peak; UC is a
        two-year change; National Student Clearinghouse and Goldman figures are
        single-year (fall 2025 / 2025–26).
      </p>
    </div>
  );
}

function Sources() {
  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Sources</h3>
      <ul className="space-y-2">
        {sourceLinks.map((s) => (
          <li key={s.url} className="text-sm">
            <a
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-700 hover:underline"
            >
              {s.label}
            </a>
          </li>
        ))}
      </ul>
      <p className="text-xs text-gray-400 mt-4">{sourceNote}</p>
    </div>
  );
}

export default function CSEnrollmentReversalStory() {
  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Lede */}
      <div className="card p-4 sm:p-6">
        <p className="text-gray-700 leading-relaxed text-base">{lede}</p>
      </div>

      <Section heading={sections.apPeak.heading} body={sections.apPeak.body} />
      <ApCsaChart />

      <Section
        heading={sections.labSciences.heading}
        body={sections.labSciences.body}
      />
      <SciIndexedChart />

      <Section heading={sections.csaVsCsp.heading} body={sections.csaVsCsp.body} />
      <CsSplitChart />

      <Section heading={sections.ucSystem.heading} body={sections.ucSystem.body} />
      <Section
        heading={sections.elitePrivates.heading}
        bullets={sections.elitePrivates.bullets}
      />

      <Section
        heading={sections.nationalContext.heading}
        body={sections.nationalContext.body}
      />
      <DeclinesBySourceChart />

      <Section
        heading={sections.whereAndWhy.heading}
        body={sections.whereAndWhy.body}
        bullets={sections.whereAndWhy.bullets}
        coda={sections.whereAndWhy.coda}
      />

      {/* Key Takeaways */}
      <div className="card p-4 sm:p-6">
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

      <Sources />
    </div>
  );
}
