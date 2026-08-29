"use client";

import { useState, useMemo } from "react";
import {
  UCYearData,
  UCDisciplineData,
  UCDiscipline,
  UC_CAMPUS_ORDER,
  UC_CAMPUS_NAMES,
  UC_CAMPUS_COLORS,
} from "@/data/uc/index";

interface Props {
  dataByYear: Record<number, UCYearData>;
  availableYears: number[];
}

function admitRate(d: UCDisciplineData): number | null {
  if (!d.admits || !d.applicants) return null;
  return d.admits / d.applicants;
}

function yieldRate(d: UCDisciplineData): number | null {
  if (!d.enrollees || !d.admits) return null;
  return d.enrollees / d.admits;
}

function fmtPct(n: number | null, decimals = 0): string {
  if (n === null) return "—";
  return `${(n * 100).toFixed(decimals)}%`;
}

function fmtNum(n: number | null): string {
  if (n === null) return "—";
  return new Intl.NumberFormat("en-US").format(n);
}

function fmtGpa(range: [number, number] | null): string {
  if (!range) return "—";
  return `${range[0].toFixed(2)} – ${range[1].toFixed(2)}`;
}

// ---- GPA Range Bar ----
function GpaBar({
  range,
  label,
  color,
  system = [3.0, 4.35],
}: {
  range: [number, number] | null;
  label: string;
  color: string;
  system?: [number, number];
}) {
  if (!range) return null;
  const span = system[1] - system[0];
  const left = ((range[0] - system[0]) / span) * 100;
  const width = ((range[1] - range[0]) / span) * 100;

  return (
    <div className="mb-3">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{label}</span>
        <span className="font-medium text-gray-700">{fmtGpa(range)}</span>
      </div>
      <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="absolute h-full rounded-full"
          style={{
            left: `${left}%`,
            width: `${width}%`,
            backgroundColor: color,
            opacity: 0.85,
          }}
        />
      </div>
      <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
        <span>{system[0].toFixed(1)}</span>
        <span>{system[1].toFixed(2)}</span>
      </div>
    </div>
  );
}

// ---- KPI Card ----
function KpiCard({
  label,
  value,
  sub,
  color,
}: {
  label: string;
  value: string;
  sub?: string;
  color: string;
}) {
  return (
    <div
      className="card p-4 sm:p-5 border-t-4 min-w-0"
      style={{ borderTopColor: color }}
    >
      <div className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1">
        {label}
      </div>
      <div className="text-2xl sm:text-3xl font-bold text-gray-800 break-words">{value}</div>
      {sub && <div className="text-sm text-gray-400 mt-0.5">{sub}</div>}
    </div>
  );
}

// ---- Discipline Table ----
type SortKey = "discipline" | "applicants" | "admits" | "enrollees" | "admitRate" | "yieldRate";

function DisciplineTable({
  disciplines,
  color,
}: {
  disciplines: Partial<Record<UCDiscipline, UCDisciplineData>>;
  color: string;
}) {
  const [sortKey, setSortKey] = useState<SortKey>("applicants");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const rows = useMemo(() => {
    const entries = Object.entries(disciplines) as [UCDiscipline, UCDisciplineData][];
    return entries
      .filter(([, d]) => d.admits !== (null as unknown as number))
      .sort(([aName, aData], [bName, bData]) => {
        let aVal: number | string;
        let bVal: number | string;
        if (sortKey === "discipline") { aVal = aName; bVal = bName; }
        else if (sortKey === "applicants") { aVal = aData.applicants ?? 0; bVal = bData.applicants ?? 0; }
        else if (sortKey === "admits") { aVal = aData.admits ?? 0; bVal = bData.admits ?? 0; }
        else if (sortKey === "enrollees") { aVal = aData.enrollees ?? 0; bVal = bData.enrollees ?? 0; }
        else if (sortKey === "admitRate") { aVal = admitRate(aData) ?? 0; bVal = admitRate(bData) ?? 0; }
        else { aVal = yieldRate(aData) ?? 0; bVal = yieldRate(bData) ?? 0; }

        if (typeof aVal === "string") {
          return sortDir === "asc"
            ? aVal.localeCompare(bVal as string)
            : (bVal as string).localeCompare(aVal);
        }
        return sortDir === "asc"
          ? (aVal as number) - (bVal as number)
          : (bVal as number) - (aVal as number);
      });
  }, [disciplines, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  const arrow = (key: SortKey) =>
    sortKey === key ? (sortDir === "desc" ? " ↓" : " ↑") : "";

  const thClass =
    "text-left text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2 cursor-pointer select-none hover:text-gray-800 whitespace-nowrap";

  return (
    <>
      <div className="md:hidden mb-4">
        <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2 mb-3">
          <select
            aria-label="Sort disciplines"
            value={sortKey}
            onChange={(event) => {
              const nextSort = event.target.value as SortKey;
              setSortKey(nextSort);
              setSortDir(nextSort === "discipline" ? "asc" : "desc");
            }}
            className="min-w-0 w-full min-h-11 border border-gray-200 rounded-lg px-3 text-sm text-gray-700 bg-white"
          >
            <option value="discipline">Discipline</option>
            <option value="applicants">Applicants</option>
            <option value="admits">Admits</option>
            <option value="admitRate">Admit rate</option>
            <option value="enrollees">Enrolled</option>
            <option value="yieldRate">Yield</option>
          </select>
          <button
            type="button"
            onClick={() => setSortDir((direction) => direction === "asc" ? "desc" : "asc")}
            className="min-h-11 min-w-11 rounded-lg border border-gray-200 bg-white text-gray-600"
            aria-label={`Sort ${sortDir === "asc" ? "descending" : "ascending"}`}
          >
            {sortDir === "asc" ? "↑" : "↓"}
          </button>
        </div>

        <div className="divide-y divide-gray-100 border-y border-gray-100">
          {rows.map(([disc, data]) => (
            <article key={`mobile-${disc}`} className="py-4 first:pt-2">
              <div className="flex items-start justify-between gap-3 mb-3">
                <h3 className="font-semibold text-gray-800 leading-snug">{disc}</h3>
                <div className="text-right flex-shrink-0">
                  <div className="text-[10px] uppercase tracking-wide text-gray-400">Admit rate</div>
                  <div className="text-lg font-bold" style={{ color }}>
                    {fmtPct(admitRate(data), 1)}
                  </div>
                </div>
              </div>
              <dl className="grid grid-cols-3 gap-2 text-sm">
                {[
                  ["Applicants", fmtNum(data.applicants)],
                  ["Admits", fmtNum(data.admits)],
                  ["Enrolled", fmtNum(data.enrollees)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <dt className="text-[10px] uppercase tracking-wide text-gray-400">{label}</dt>
                    <dd className="font-medium text-gray-700 mt-0.5">{value}</dd>
                  </div>
                ))}
              </dl>
              <dl className="grid grid-cols-3 gap-2 text-sm mt-3 pt-3 border-t border-gray-100">
                <div>
                  <dt className="text-[10px] uppercase tracking-wide text-gray-400">Yield</dt>
                  <dd className="font-medium text-gray-700 mt-0.5">{fmtPct(yieldRate(data), 1)}</dd>
                </div>
                <div>
                  <dt className="text-[10px] uppercase tracking-wide text-gray-400">Admit GPA</dt>
                  <dd className="font-medium text-gray-700 mt-0.5 whitespace-nowrap">{fmtGpa(data.admitGpaRange)}</dd>
                </div>
                <div>
                  <dt className="text-[10px] uppercase tracking-wide text-gray-400">Enrollee GPA</dt>
                  <dd className="font-medium text-gray-700 mt-0.5 whitespace-nowrap">{fmtGpa(data.enrolleeGpaRange)}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </div>

      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className={thClass} onClick={() => toggleSort("discipline")}>
              Discipline{arrow("discipline")}
            </th>
            <th className={`${thClass} text-right`} onClick={() => toggleSort("applicants")}>
              Applicants{arrow("applicants")}
            </th>
            <th className={`${thClass} text-right`} onClick={() => toggleSort("admits")}>
              Admits{arrow("admits")}
            </th>
            <th className={`${thClass} text-right`} onClick={() => toggleSort("admitRate")}>
              Admit Rate{arrow("admitRate")}
            </th>
            <th className={`${thClass} text-right`} onClick={() => toggleSort("enrollees")}>
              Enrolled{arrow("enrollees")}
            </th>
            <th className={`${thClass} text-right`} onClick={() => toggleSort("yieldRate")}>
              Yield{arrow("yieldRate")}
            </th>
            <th className={`${thClass} text-right`}>Admit GPA (25–75)</th>
            <th className={`${thClass} text-right`}>Enrollee GPA (25–75)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([disc, data]) => (
            <tr key={disc} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
              <td className="py-2.5 pr-4 font-medium text-gray-800">{disc}</td>
              <td className="py-2.5 text-right text-gray-600">{fmtNum(data.applicants)}</td>
              <td className="py-2.5 text-right text-gray-600">{fmtNum(data.admits)}</td>
              <td className="py-2.5 text-right font-semibold" style={{ color }}>
                {fmtPct(admitRate(data), 1)}
              </td>
              <td className="py-2.5 text-right text-gray-600">{fmtNum(data.enrollees)}</td>
              <td className="py-2.5 text-right text-gray-600">{fmtPct(yieldRate(data), 1)}</td>
              <td className="py-2.5 text-right text-gray-500 text-xs">{fmtGpa(data.admitGpaRange)}</td>
              <td className="py-2.5 text-right text-gray-500 text-xs">{fmtGpa(data.enrolleeGpaRange)}</td>
            </tr>
          ))}
        </tbody>
        </table>
      </div>
    </>
  );
}

// ---- Side Panel (used in both Explore and Compare) ----
function CampusPanel({
  yearData,
  campusCode,
  discipline,
  color,
  label,
}: {
  yearData: UCYearData;
  campusCode: string;
  discipline: UCDiscipline | "All";
  color: string;
  label?: string;
}) {
  const campus = yearData.campuses[campusCode];
  if (!campus) return null;

  const data: UCDisciplineData | undefined =
    discipline === "All"
      ? campus.overall
      : campus.disciplines[discipline as UCDiscipline];

  const ar = data ? admitRate(data) : null;
  const yr = data ? yieldRate(data) : null;

  return (
    <div>
      {label && (
        <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
          {label}
        </div>
      )}
      <div className="text-xl font-bold mb-0.5" style={{ color }}>
        {UC_CAMPUS_NAMES[campusCode]}
      </div>
      <div className="text-sm text-gray-500 mb-5">
        {discipline === "All" ? "All Disciplines" : discipline}
      </div>

      {!data ? (
        <div className="text-gray-400 text-sm italic">No data for this selection.</div>
      ) : (
        <>
          <div className="grid grid-cols-1 min-[360px]:grid-cols-2 gap-3 mb-5">
            <KpiCard label="Applicants" value={fmtNum(data.applicants)} color={color} />
            <KpiCard label="Admits" value={fmtNum(data.admits)} color={color} />
            <KpiCard
              label="Admit Rate"
              value={fmtPct(ar, 1)}
              color={color}
            />
            <KpiCard
              label="Yield Rate"
              value={fmtPct(yr, 1)}
              sub={data.enrollees ? `${fmtNum(data.enrollees)} enrolled` : undefined}
              color={color}
            />
          </div>
          <div className="card p-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">
              GPA Ranges (UC-calculated, 25th–75th pctl)
            </div>
            <GpaBar range={data.admitGpaRange} label="Admit GPA" color={color} />
            <GpaBar range={data.enrolleeGpaRange} label="Enrollee GPA" color={color} />
          </div>
        </>
      )}
    </div>
  );
}

// ---- Main Page ----
export default function UCPageClient({ dataByYear, availableYears }: Props) {
  const [selectedYear, setSelectedYear] = useState(availableYears[0]);
  const [mode, setMode] = useState<"explore" | "compare">("explore");

  // Explore mode state
  const [exploreCampus, setExploreCampus] = useState("UCB");
  const [exploreDiscipline, setExploreDiscipline] = useState<UCDiscipline | "All">("All");

  // Compare mode state
  const [compareACode, setCompareACode] = useState("UCB");
  const [compareADisc, setCompareADisc] = useState<UCDiscipline | "All">("All");
  const [compareAYear, setCompareAYear] = useState(availableYears[0]);
  const [compareBCode, setCompareBCode] = useState("UCLA");
  const [compareBDisc, setCompareBDisc] = useState<UCDiscipline | "All">("All");
  const [compareBYear, setCompareBYear] = useState(availableYears[0]);

  const yearData = dataByYear[selectedYear];
  const campusCodes = UC_CAMPUS_ORDER.filter(c => yearData.campuses[c]);

  const exploreCampusData = yearData.campuses[exploreCampus];
  const allDisciplines = exploreCampusData
    ? (Object.keys(exploreCampusData.disciplines) as UCDiscipline[]).sort()
    : [];

  const colorA = UC_CAMPUS_COLORS[compareACode] ?? "#003262";
  const colorB = UC_CAMPUS_COLORS[compareBCode] ?? "#2D68C4";
  const exploreColor = UC_CAMPUS_COLORS[exploreCampus] ?? "#003262";

  const yearDataA = dataByYear[compareAYear];
  const yearDataB = dataByYear[compareBYear];
  const campusCodesA = UC_CAMPUS_ORDER.filter(c => yearDataA.campuses[c]);
  const campusCodesB = UC_CAMPUS_ORDER.filter(c => yearDataB.campuses[c]);

  // Available disciplines for compare selectors
  const discA = yearDataA.campuses[compareACode]
    ? (Object.keys(yearDataA.campuses[compareACode].disciplines) as UCDiscipline[]).sort()
    : [];
  const discB = yearDataB.campuses[compareBCode]
    ? (Object.keys(yearDataB.campuses[compareBCode].disciplines) as UCDiscipline[]).sort()
    : [];

  const selectClass =
    "w-full sm:w-auto min-w-0 min-h-11 border border-gray-200 rounded-md px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-14 px-4 text-center text-white">
        <h1 className="text-3xl md:text-4xl font-bold mb-3">UC Campus Explorer</h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto">
          Admissions data across all 9 UC campuses
        </p>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6 sm:py-8">

        {/* Controls */}
        <div className="card p-4 mb-6 flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-3">
          {/* Mode toggle */}
          <div className="flex w-full sm:w-auto rounded-md border border-gray-200 overflow-hidden">
            {(["explore", "compare"] as const).map(m => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 sm:flex-none min-h-11 px-4 py-2 text-sm font-medium capitalize transition-colors ${
                  mode === m
                    ? "bg-gray-800 text-white"
                    : "bg-white text-gray-600 hover:bg-gray-50"
                }`}
              >
                {m}
              </button>
            ))}
          </div>

          {/* Year selector — only in explore mode */}
          {availableYears.length > 1 && mode === "explore" && (
            <select
              className={selectClass}
              value={selectedYear}
              onChange={e => setSelectedYear(Number(e.target.value))}
            >
              {availableYears.map(y => (
                <option key={y} value={y}>
                  Fall {y}
                </option>
              ))}
            </select>
          )}

          {mode === "explore" && (
            <>
              <select
                className={selectClass}
                value={exploreCampus}
                onChange={e => { setExploreCampus(e.target.value); setExploreDiscipline("All"); }}
              >
                {campusCodes.map(c => (
                  <option key={c} value={c}>{UC_CAMPUS_NAMES[c]}</option>
                ))}
              </select>
              <select
                className={selectClass}
                value={exploreDiscipline}
                onChange={e => setExploreDiscipline(e.target.value as UCDiscipline | "All")}
              >
                <option value="All">All Disciplines</option>
                {allDisciplines.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </>
          )}
        </div>

        {/* ---- EXPLORE MODE ---- */}
        {mode === "explore" && (
          <>
            {/* KPI + GPA */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-2 grid grid-cols-1 min-[360px]:grid-cols-2 md:grid-cols-4 gap-4">
                {(() => {
                  const d =
                    exploreDiscipline === "All"
                      ? exploreCampusData?.overall
                      : exploreCampusData?.disciplines[exploreDiscipline as UCDiscipline];
                  if (!d) return <div className="col-span-4 text-gray-400 italic text-sm">No data for this selection.</div>;
                  return (
                    <>
                      <KpiCard label="Applicants" value={fmtNum(d.applicants)} color={exploreColor} />
                      <KpiCard label="Admits" value={fmtNum(d.admits)} color={exploreColor} />
                      <KpiCard label="Admit Rate" value={fmtPct(admitRate(d), 1)} color={exploreColor} />
                      <KpiCard
                        label="Yield Rate"
                        value={fmtPct(yieldRate(d), 1)}
                        sub={d.enrollees ? `${fmtNum(d.enrollees)} enrolled` : undefined}
                        color={exploreColor}
                      />
                    </>
                  );
                })()}
              </div>
              <div className="card p-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">
                  GPA Ranges (25th–75th pctl)
                </div>
                {(() => {
                  const d =
                    exploreDiscipline === "All"
                      ? exploreCampusData?.overall
                      : exploreCampusData?.disciplines[exploreDiscipline as UCDiscipline];
                  if (!d) return <div className="text-gray-400 text-sm italic">—</div>;
                  return (
                    <>
                      <GpaBar range={d.admitGpaRange} label="Admit GPA" color={exploreColor} />
                      <GpaBar range={d.enrolleeGpaRange} label="Enrollee GPA" color={exploreColor} />
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Discipline table — only show when "All" selected */}
            {exploreDiscipline === "All" && exploreCampusData && (
              <div className="card p-4 sm:p-6">
                <h2 className="text-base font-semibold text-gray-800 mb-4">
                  By Discipline — {UC_CAMPUS_NAMES[exploreCampus]}
                </h2>
                <DisciplineTable
                  disciplines={exploreCampusData.disciplines}
                  color={exploreColor}
                />
                <p className="text-xs text-gray-400 mt-4">
                  Disciplines with fewer than 5 applicants or fewer than 3 admits/enrollees are not shown.
                  Admit rate = admits ÷ applicants. Yield = enrolled ÷ admits.
                </p>
              </div>
            )}

            {/* All-campus comparison table */}
            <div className="card p-4 sm:p-6 mt-6">
              <h2 className="text-base font-semibold text-gray-800 mb-4">
                All Campuses — {exploreDiscipline === "All" ? "Overall" : exploreDiscipline}
              </h2>
              <div className="md:hidden divide-y divide-gray-100 border-y border-gray-100">
                {campusCodes.map(code => {
                  const camp = yearData.campuses[code];
                  const d = exploreDiscipline === "All"
                    ? camp.overall
                    : camp.disciplines[exploreDiscipline as UCDiscipline];
                  const isSel = code === exploreCampus;
                  const color = UC_CAMPUS_COLORS[code];
                  return (
                    <button
                      type="button"
                      key={`mobile-${code}`}
                      className={`w-full min-h-11 py-4 text-left ${isSel ? "bg-blue-50" : ""}`}
                      onClick={() => setExploreCampus(code)}
                    >
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <span className="font-semibold leading-snug" style={{ color }}>
                          {UC_CAMPUS_NAMES[code]}
                        </span>
                        <span className="text-right flex-shrink-0">
                          <span className="block text-[10px] uppercase tracking-wide text-gray-400">Admit rate</span>
                          <span className="block text-lg font-bold" style={{ color }}>
                            {d ? fmtPct(admitRate(d), 1) : "—"}
                          </span>
                        </span>
                      </div>
                      <span className="grid grid-cols-3 gap-2 text-sm">
                        {[
                          ["Applicants", d ? fmtNum(d.applicants) : "—"],
                          ["Admits", d ? fmtNum(d.admits) : "—"],
                          ["Enrolled", d ? fmtNum(d.enrollees) : "—"],
                        ].map(([label, value]) => (
                          <span key={label}>
                            <span className="block text-[10px] uppercase tracking-wide text-gray-400">{label}</span>
                            <span className="block font-medium text-gray-700 mt-0.5">{value}</span>
                          </span>
                        ))}
                      </span>
                      <span className="grid grid-cols-3 gap-2 text-sm mt-3 pt-3 border-t border-gray-100">
                        <span>
                          <span className="block text-[10px] uppercase tracking-wide text-gray-400">Yield</span>
                          <span className="block font-medium text-gray-700 mt-0.5">{d ? fmtPct(yieldRate(d), 1) : "—"}</span>
                        </span>
                        <span>
                          <span className="block text-[10px] uppercase tracking-wide text-gray-400">Admit GPA</span>
                          <span className="block font-medium text-gray-700 mt-0.5 whitespace-nowrap">{d ? fmtGpa(d.admitGpaRange) : "—"}</span>
                        </span>
                        <span>
                          <span className="block text-[10px] uppercase tracking-wide text-gray-400">Enrollee GPA</span>
                          <span className="block font-medium text-gray-700 mt-0.5 whitespace-nowrap">{d ? fmtGpa(d.enrolleeGpaRange) : "—"}</span>
                        </span>
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="hidden md:block overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2">Campus</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2">Applicants</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2">Admits</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2">Admit Rate</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2">Enrolled</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2">Yield</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2 hidden md:table-cell">Admit GPA (25–75)</th>
                      <th className="text-right text-xs font-semibold uppercase tracking-wide text-gray-500 pb-2 hidden md:table-cell">Enrollee GPA (25–75)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {campusCodes.map(code => {
                      const camp = yearData.campuses[code];
                      const d =
                        exploreDiscipline === "All"
                          ? camp.overall
                          : camp.disciplines[exploreDiscipline as UCDiscipline];
                      const isSel = code === exploreCampus;
                      const color = UC_CAMPUS_COLORS[code];
                      return (
                        <tr
                          key={code}
                          className={`border-b border-gray-100 transition-colors cursor-pointer ${
                            isSel ? "bg-blue-50" : "hover:bg-gray-50"
                          }`}
                          onClick={() => setExploreCampus(code)}
                        >
                          <td className="py-2.5 pr-4">
                            <span
                              className="font-semibold"
                              style={{ color }}
                            >
                              {UC_CAMPUS_NAMES[code]}
                            </span>
                          </td>
                          <td className="py-2.5 text-right text-gray-600">{d ? fmtNum(d.applicants) : "—"}</td>
                          <td className="py-2.5 text-right text-gray-600">{d ? fmtNum(d.admits) : "—"}</td>
                          <td className="py-2.5 text-right font-semibold" style={{ color }}>
                            {d ? fmtPct(admitRate(d), 1) : "—"}
                          </td>
                          <td className="py-2.5 text-right text-gray-600">{d ? fmtNum(d.enrollees) : "—"}</td>
                          <td className="py-2.5 text-right text-gray-600">{d ? fmtPct(yieldRate(d), 1) : "—"}</td>
                          <td className="py-2.5 text-right text-gray-500 text-xs hidden md:table-cell">{d ? fmtGpa(d.admitGpaRange) : "—"}</td>
                          <td className="py-2.5 text-right text-gray-500 text-xs hidden md:table-cell">{d ? fmtGpa(d.enrolleeGpaRange) : "—"}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="text-xs text-gray-400 mt-3">Select a campus to update the summary above.</p>
            </div>
          </>
        )}

        {/* ---- COMPARE MODE ---- */}
        {mode === "compare" && (
          <>
            {/* Compare selectors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {/* Panel A */}
              <div className="card p-4">
                <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Side A</div>
                <div className="flex flex-col gap-2">
                  <select
                    className={selectClass}
                    value={compareAYear}
                    onChange={e => setCompareAYear(Number(e.target.value))}
                  >
                    {availableYears.map(y => (
                      <option key={y} value={y}>Fall {y}</option>
                    ))}
                  </select>
                  <select
                    className={selectClass}
                    value={compareACode}
                    onChange={e => { setCompareACode(e.target.value); setCompareADisc("All"); }}
                  >
                    {campusCodesA.map(c => (
                      <option key={c} value={c}>{UC_CAMPUS_NAMES[c]}</option>
                    ))}
                  </select>
                  <select
                    className={selectClass}
                    value={compareADisc}
                    onChange={e => setCompareADisc(e.target.value as UCDiscipline | "All")}
                  >
                    <option value="All">All Disciplines (Overall)</option>
                    {discA.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>
              {/* Panel B */}
              <div className="card p-4">
                <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Side B</div>
                <div className="flex flex-col gap-2">
                  <select
                    className={selectClass}
                    value={compareBYear}
                    onChange={e => setCompareBYear(Number(e.target.value))}
                  >
                    {availableYears.map(y => (
                      <option key={y} value={y}>Fall {y}</option>
                    ))}
                  </select>
                  <select
                    className={selectClass}
                    value={compareBCode}
                    onChange={e => { setCompareBCode(e.target.value); setCompareBDisc("All"); }}
                  >
                    {campusCodesB.map(c => (
                      <option key={c} value={c}>{UC_CAMPUS_NAMES[c]}</option>
                    ))}
                  </select>
                  <select
                    className={selectClass}
                    value={compareBDisc}
                    onChange={e => setCompareBDisc(e.target.value as UCDiscipline | "All")}
                  >
                    <option value="All">All Disciplines (Overall)</option>
                    {discB.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>
            </div>

            {/* Side by side panels */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card p-4 sm:p-6 min-w-0">
                <CampusPanel
                  yearData={yearDataA}
                  campusCode={compareACode}
                  discipline={compareADisc}
                  color={colorA}
                />
              </div>
              <div className="card p-4 sm:p-6 min-w-0">
                <CampusPanel
                  yearData={yearDataB}
                  campusCode={compareBCode}
                  discipline={compareBDisc}
                  color={colorB}
                />
              </div>
            </div>

            {/* Delta row */}
            {(() => {
              const dA =
                compareADisc === "All"
                  ? yearDataA.campuses[compareACode]?.overall
                  : yearDataA.campuses[compareACode]?.disciplines[compareADisc as UCDiscipline];
              const dB =
                compareBDisc === "All"
                  ? yearDataB.campuses[compareBCode]?.overall
                  : yearDataB.campuses[compareBCode]?.disciplines[compareBDisc as UCDiscipline];
              if (!dA || !dB) return null;
              const arA = admitRate(dA);
              const arB = admitRate(dB);
              const yrA = yieldRate(dA);
              const yrB = yieldRate(dB);
              const delta = (a: number | null, b: number | null) => {
                if (a === null || b === null) return "—";
                const d = a - b;
                return `${d >= 0 ? "+" : ""}${(d * 100).toFixed(1)} pp`;
              };
              return (
                <div className="card p-4 sm:p-5 mt-4">
                  <div className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">
                    Difference (A minus B)
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    {[
                      { label: "Admit Rate", val: delta(arA, arB) },
                      { label: "Yield Rate", val: delta(yrA, yrB) },
                      { label: "Admit GPA 25th", val: dA.admitGpaRange && dB.admitGpaRange ? `${(dA.admitGpaRange[0] - dB.admitGpaRange[0]).toFixed(2)}` : "—" },
                      { label: "Admit GPA 75th", val: dA.admitGpaRange && dB.admitGpaRange ? `${(dA.admitGpaRange[1] - dB.admitGpaRange[1]).toFixed(2)}` : "—" },
                    ].map(({ label, val }) => (
                      <div key={label}>
                        <div className="text-xs text-gray-500 mb-1">{label}</div>
                        <div className="text-lg font-bold text-gray-800">{val}</div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}
          </>
        )}

        <p className="text-xs text-gray-400 text-center mt-8">
          Source: UC Information Center · {mode === "compare" ? `Fall ${compareAYear} / Fall ${compareBYear}` : `Fall ${selectedYear}`} · GPA is UC-calculated (may exceed 4.0 with honors courses)
        </p>
      </div>
    </div>
  );
}
