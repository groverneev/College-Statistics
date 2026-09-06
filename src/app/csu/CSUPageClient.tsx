"use client";

import { useMemo, useState } from "react";
import {
  CSU_DISCIPLINE_FALL,
  CSU_EARLIEST_FALL,
  CSU_LATEST_FALL,
  CSU_LEVEL_LABELS,
  admitRate,
  areaLabel,
  campusArea,
  campusAreasFor,
  campusLevelTotals,
  campusName,
  csuAreasByVolume,
  csuCampusesByName,
  csuCampusesBySelectivity,
  csuCountiesByRate,
  csuData,
  csuMatrixAreas,
  csuStatewideEarliest,
  csuStatewideLatest,
  yieldRate,
  type CSUCampusArea,
  type CSULevel,
} from "@/data/csu";
import {
  BAR_RAMP,
  BarList,
  GroupedBars,
  HEAT_RAMP,
  Legend,
  LineChart,
  POPPY,
  Panel,
  RampKey,
  Scatter,
  StatTiles,
  TEAL,
  TooltipProvider,
  barFill,
  fmtCompact,
  fmtNum,
  fmtPct,
  heatFill,
  inkOn,
  useHover,
  type BarRow,
  type ScatterPoint,
} from "./charts";

const TABS = [
  { id: "system", label: "Systemwide" },
  { id: "campus", label: "Campus profile" },
  { id: "matrix", label: "Major matrix" },
  { id: "pipeline", label: "California pipeline" },
] as const;

type TabId = (typeof TABS)[number]["id"];

const LATEST = String(CSU_LATEST_FALL);
const EARLIEST = String(CSU_EARLIEST_FALL);

/** Campuses admitting fewer than half their applicants get the accent colour. */
const SELECTIVE_THRESHOLD = 50;

function signed(n: number, digits = 1): string {
  return `${n >= 0 ? "+" : ""}${n.toFixed(digits)}`;
}

function Delta({ value, suffix }: { value: number; suffix: string }) {
  return (
    <>
      <span
        className="font-semibold"
        style={{ color: value >= 0 ? "#0E6584" : POPPY }}
      >
        {signed(value)}
        {suffix}
      </span>{" "}
    </>
  );
}

// ---------------------------------------------------------------------------
// Systemwide
// ---------------------------------------------------------------------------

function FunnelStage({
  label,
  value,
  total,
  color,
  paleInk,
  meta,
}: {
  label: string;
  value: number;
  total: number;
  color: string;
  paleInk?: boolean;
  meta?: string;
}) {
  const width = (value / total) * 100;
  // The meta line is pinned to the right edge of the track rather than to the
  // end of the fill, so a nearly full bar cannot push it off the panel. It sits
  // over the fill on wide bars, so it takes its ink from whatever is behind it.
  const metaOverFill = width > 70;
  return (
    <div className="grid items-center gap-3" style={{ gridTemplateColumns: "6.5rem 1fr" }}>
      <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">{label}</div>
      <div className="relative h-9 overflow-hidden rounded bg-gray-100">
        <div
          className="absolute inset-y-0 left-0 flex items-center justify-between gap-3 rounded px-3.5"
          style={{ width: `${width}%`, backgroundColor: color }}
        >
          <span
            className="text-base font-semibold tabular-nums"
            style={{ color: paleInk ? "#1a1a1a" : "#ffffff" }}
          >
            {fmtNum(value)}
          </span>
          {meta && metaOverFill && (
            <span
              className="hidden truncate text-xs sm:block"
              style={{ color: paleInk ? "#4b5563" : "#DCEAF0" }}
            >
              {meta}
            </span>
          )}
        </div>
        {meta && !metaOverFill && (
          <div className="absolute right-3.5 top-1/2 hidden -translate-y-1/2 truncate text-xs text-gray-500 sm:block">
            {meta}
          </div>
        )}
      </div>
    </div>
  );
}

function SystemwideView() {
  const latest = csuData.system[LATEST];
  const earliest = csuData.system[EARLIEST];

  const applied = latest.applied ?? 0;
  const admitted = latest.admitted ?? 0;
  const enrolled = latest.enrolled ?? 0;
  const rate = admitRate(latest) ?? 0;
  const priorRate = admitRate(earliest) ?? 0;
  const yieldNow = yieldRate(latest);

  const appGrowth = 100 * (applied / (earliest.applied ?? applied) - 1);
  const enrGrowth = 100 * (enrolled / (earliest.enrolled ?? enrolled) - 1);

  const rows: BarRow[] = csuCampusesBySelectivity.map((key) => {
    const term = csuData.campuses[key][LATEST];
    const campusRate = admitRate(term) ?? 0;
    return {
      key,
      label: campusName(key),
      value: campusRate,
      display: fmtPct(campusRate),
      fill: campusRate < SELECTIVE_THRESHOLD ? POPPY : TEAL,
      emphasis: campusRate < SELECTIVE_THRESHOLD,
      tooltip: {
        title: campusName(key),
        rows: [
          { label: "Applied", value: fmtNum(term.applied) },
          { label: "Admitted", value: fmtNum(term.admitted) },
          { label: "Enrolled", value: fmtNum(term.enrolled) },
          { label: "Admit rate", value: fmtPct(campusRate) },
          { label: "Yield", value: fmtPct(yieldRate(term)) },
        ],
      },
    };
  });

  return (
    <div className="flex flex-col gap-4">
      <StatTiles
        tiles={[
          {
            label: "Applications",
            value: fmtNum(applied),
            detail: (
              <>
                <Delta value={appGrowth} suffix="%" />since Fall {CSU_EARLIEST_FALL}
              </>
            ),
          },
          {
            label: "Admit rate",
            value: fmtPct(rate),
            detail: (
              <>
                <Delta value={rate - priorRate} suffix=" pts" />— the CSU has grown more open
              </>
            ),
          },
          {
            label: "Yield",
            value: fmtPct(yieldNow),
            detail: "Share of admitted students who enrolled",
          },
          {
            label: "New students",
            value: fmtNum(enrolled),
            detail: (
              <>
                <Delta value={enrGrowth} suffix="%" />since Fall {CSU_EARLIEST_FALL}
              </>
            ),
          },
        ]}
      />

      <Panel
        title={`From application to enrollment, Fall ${CSU_LATEST_FALL}`}
        note="Bar length is proportional to headcount. Percentages are of the preceding stage."
      >
        <div className="flex flex-col gap-2.5">
          <FunnelStage label="Applied" value={applied} total={applied} color={HEAT_RAMP[7]} />
          <FunnelStage
            label="Admitted"
            value={admitted}
            total={applied}
            color={HEAT_RAMP[5]}
            meta={`${fmtPct(rate)} of applicants · ${fmtNum(applied - admitted)} denied`}
          />
          <FunnelStage
            label="Enrolled"
            value={enrolled}
            total={applied}
            color={HEAT_RAMP[3]}
            paleInk
            meta={`${fmtPct(yieldNow)} of admits · ${fmtNum(admitted - enrolled)} chose elsewhere`}
          />
        </div>
      </Panel>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Applications received" note="Systemwide, all campuses">
          <LineChart
            points={csuData.fallYears.map((y) => ({
              key: `’${String(y).slice(2)}`,
              value: csuData.system[String(y)].applied ?? 0,
            }))}
            formatValue={fmtCompact}
            label="Applications by year"
          />
        </Panel>
        <Panel title="Admit rate" note="Admitted as a share of applicants">
          <LineChart
            points={csuData.fallYears.map((y) => ({
              key: `’${String(y).slice(2)}`,
              value: admitRate(csuData.system[String(y)]) ?? 0,
            }))}
            color={POPPY}
            formatValue={(n) => `${n.toFixed(0)}%`}
            label="Admit rate by year"
          />
        </Panel>
      </div>

      <Panel
        title="Every campus, ranked by selectivity"
        aside={
          <Legend
            items={[
              { label: "Admit rate", color: TEAL },
              { label: "Admits fewer than half of applicants", color: POPPY },
            ]}
          />
        }
        footnote={`Fall ${CSU_LATEST_FALL}, all entry levels. CalStateTEACH is a systemwide credential program rather than a campus and is not ranked.`}
      >
        <BarList rows={rows} max={100} labelWidth="10.5rem" />
      </Panel>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Campus profile
// ---------------------------------------------------------------------------

function LevelBar({ totals, level }: { totals: CSUCampusArea; level: CSULevel }) {
  const rate = admitRate(totals);
  const color = level === "F" ? TEAL : POPPY;
  const hover = useHover({
    title: CSU_LEVEL_LABELS[level],
    rows: [
      { label: "Applied", value: fmtNum(totals.applied) },
      { label: "Admitted", value: fmtNum(totals.admitted) },
      { label: "Enrolled", value: fmtNum(totals.enrolled) },
      { label: "Admit rate", value: fmtPct(rate) },
    ],
  });

  return (
    <div className="pb-3.5 pt-1.5">
      <div className="mb-1.5 flex items-baseline justify-between gap-3">
        <span className="text-xs font-semibold text-gray-700">{CSU_LEVEL_LABELS[level]}</span>
        <span className="text-xs tabular-nums text-gray-500">
          {fmtNum(totals.applied)} applied · {fmtPct(rate)} admitted
        </span>
      </div>
      <div className="relative h-5 overflow-hidden rounded-sm" {...hover}>
        <div className="absolute inset-0" style={{ backgroundColor: color, opacity: 0.22 }} />
        <div
          className="absolute inset-y-0 left-0"
          style={{ width: `${rate ?? 0}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

function CampusView() {
  const [selected, setSelected] = useState(csuCampusesBySelectivity[0]);

  const latest = csuData.campuses[selected][LATEST];
  const earliest = csuData.campuses[selected][EARLIEST];
  const rate = admitRate(latest) ?? 0;
  const priorRate = admitRate(earliest) ?? 0;
  const systemRate = admitRate(csuData.system[LATEST]) ?? 0;
  const appGrowth = 100 * ((latest.applied ?? 0) / (earliest.applied ?? 1) - 1);

  const areaRows: BarRow[] = useMemo(
    () =>
      campusAreasFor(selected, "F").map((row) => {
        const areaRate = admitRate(row) ?? 0;
        return {
          key: row.area,
          label: areaLabel(row.area),
          value: areaRate,
          display: fmtPct(areaRate),
          fill: areaRate < SELECTIVE_THRESHOLD ? POPPY : TEAL,
          emphasis: areaRate < SELECTIVE_THRESHOLD,
          tooltip: {
            title: areaLabel(row.area),
            rows: [
              { label: "Applied", value: fmtNum(row.applied) },
              { label: "Admitted", value: fmtNum(row.admitted) },
              { label: "Enrolled", value: fmtNum(row.enrolled) },
              { label: "Admit rate", value: fmtPct(areaRate) },
            ],
          },
        };
      }),
    [selected]
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-1.5">
        {csuCampusesByName.map((key) => {
          const active = key === selected;
          return (
            <button
              key={key}
              type="button"
              onClick={() => setSelected(key)}
              aria-pressed={active}
              className={`rounded-full border px-3 py-1.5 text-xs transition-colors ${
                active
                  ? "border-transparent text-white"
                  : "border-gray-200 bg-white text-gray-600 hover:border-gray-400 hover:text-gray-900"
              }`}
              style={active ? { backgroundColor: "#08465A" } : undefined}
            >
              {campusName(key)}
            </button>
          );
        })}
      </div>

      <StatTiles
        tiles={[
          {
            label: "Applications",
            value: fmtNum(latest.applied),
            detail: (
              <>
                <Delta value={appGrowth} suffix="%" />since Fall {CSU_EARLIEST_FALL}
              </>
            ),
          },
          {
            label: "Admit rate",
            value: fmtPct(rate),
            detail: `${Math.abs(rate - systemRate).toFixed(1)} pts ${
              rate < systemRate ? "below" : "above"
            } the systemwide ${fmtPct(systemRate)}`,
          },
          {
            label: "Yield",
            value: fmtPct(yieldRate(latest)),
            detail: `${fmtNum(latest.enrolled)} of ${fmtNum(latest.admitted)} admits enrolled`,
          },
          {
            label: "Admit rate change",
            value: `${signed(rate - priorRate)} pts`,
            detail: `From ${fmtPct(priorRate)} in Fall ${CSU_EARLIEST_FALL}`,
          },
        ]}
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel
          title={`${campusName(selected)} — five-year volume`}
          aside={
            <Legend
              items={[
                { label: "Applied", color: HEAT_RAMP[7] },
                { label: "Admitted", color: HEAT_RAMP[5] },
                { label: "Enrolled", color: HEAT_RAMP[3] },
              ]}
            />
          }
        >
          <GroupedBars
            groups={csuData.fallYears.map((y) => ({
              key: `Fall ’${String(y).slice(2)}`,
              values: csuData.campuses[selected][String(y)] as unknown as Record<string, number | null>,
            }))}
            series={[
              { key: "applied", name: "Applied", color: HEAT_RAMP[7] },
              { key: "admitted", name: "Admitted", color: HEAT_RAMP[5] },
              { key: "enrolled", name: "Enrolled", color: HEAT_RAMP[3] },
            ]}
            formatValue={fmtCompact}
            label={`Applied, admitted and enrolled at ${campusName(selected)} by year`}
          />
        </Panel>

        <Panel
          title={`Freshmen and transfers, Fall ${CSU_DISCIPLINE_FALL}`}
          aside={
            <Legend
              items={[
                { label: "First-time freshmen", color: TEAL },
                { label: "Transfers", color: POPPY },
              ]}
            />
          }
          footnote="Bar fill is the admit rate; the pale track is 100% of applicants to that entry level."
        >
          <LevelBar totals={campusLevelTotals(selected, "F")} level="F" />
          <LevelBar totals={campusLevelTotals(selected, "U")} level="U" />
        </Panel>
      </div>

      <Panel
        title={`Where it is hardest to get in at ${campusName(selected)}`}
        aside={
          <Legend
            items={[
              { label: "Admit rate", color: TEAL },
              { label: "Under 50%", color: POPPY },
            ]}
          />
        }
        footnote={`First-time freshmen, Fall ${CSU_DISCIPLINE_FALL}, by broad discipline area. Hover a row for counts.`}
      >
        {areaRows.length > 0 ? (
          <BarList rows={areaRows} max={100} />
        ) : (
          <p className="text-xs text-gray-400">
            The CSU does not publish discipline-level figures for this campus.
          </p>
        )}
      </Panel>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Major matrix
// ---------------------------------------------------------------------------

function HeatCell({ campus, area, level }: { campus: string; area: string; level: CSULevel }) {
  const row = campusArea(campus, area, level);
  const rate = row ? admitRate(row) : null;
  const hover = useHover(
    row && rate != null
      ? {
          title: `${campusName(campus)} · ${areaLabel(area)}`,
          rows: [
            { label: "Applied", value: fmtNum(row.applied) },
            { label: "Admitted", value: fmtNum(row.admitted) },
            { label: "Enrolled", value: fmtNum(row.enrolled) },
            { label: "Admit rate", value: fmtPct(rate) },
          ],
        }
      : null
  );

  if (!row || rate == null) {
    return (
      <div
        className="h-6 rounded-sm"
        style={{
          background: "repeating-linear-gradient(45deg,#F4F7F8 0 4px,#EAEFF2 4px 8px)",
        }}
        title={`${campusName(campus)} has no ${areaLabel(area)} program at this entry level`}
      />
    );
  }

  const fill = heatFill(rate);
  return (
    <div
      className="flex h-6 items-center justify-center rounded-sm text-[10px] font-medium tabular-nums hover:outline hover:outline-2 hover:-outline-offset-2"
      style={{ backgroundColor: fill, color: inkOn(fill), outlineColor: POPPY }}
      {...hover}
    >
      {Math.round(rate)}
    </div>
  );
}

function MatrixView() {
  const [level, setLevel] = useState<CSULevel>("F");

  const largest: BarRow[] = csuData.largest.slice(0, 16).map((p) => ({
    key: `${p.campus}|${p.major}`,
    label: `${p.major} — ${campusName(p.campus)}`,
    value: p.applied,
    display: fmtNum(p.applied),
    fill: barFill(p.admitRate),
    tooltip: {
      title: p.major,
      rows: [
        { label: "Campus", value: campusName(p.campus) },
        { label: "Applied", value: fmtNum(p.applied) },
        { label: "Admitted", value: fmtNum(p.admitted) },
        { label: "Admit rate", value: fmtPct(p.admitRate) },
      ],
    },
  }));

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-4">
        <div className="inline-flex overflow-hidden rounded-lg border border-gray-200 bg-white">
          {(["F", "U"] as CSULevel[]).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setLevel(option)}
              aria-pressed={level === option}
              className={`px-3.5 py-2 text-xs font-semibold transition-colors ${
                level === option ? "text-white" : "text-gray-500 hover:text-gray-800"
              }`}
              style={level === option ? { backgroundColor: "#08465A" } : undefined}
            >
              {CSU_LEVEL_LABELS[option]}
            </button>
          ))}
        </div>
        <RampKey />
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
        <Panel
          title={`Admit rate by campus and discipline, Fall ${CSU_DISCIPLINE_FALL}`}
          note="Each cell is one campus’s admit rate in that area. Hatched cells have no program."
          footnote="Numbers in cells are admit rates in percent. Rows are ordered by overall campus selectivity; columns by systemwide application volume."
        >
          <div className="overflow-x-auto pb-1">
            <div
              className="grid min-w-[46rem] gap-0.5"
              style={{ gridTemplateColumns: `8.5rem repeat(${csuMatrixAreas.length}, minmax(2.4rem, 1fr))` }}
            >
              <div className="sticky left-0 z-10 bg-white" />
              {csuMatrixAreas.map((area) => (
                <div
                  key={area}
                  className="flex h-[4.9rem] items-end whitespace-nowrap pb-1 text-[10px] font-semibold uppercase tracking-wide text-gray-500"
                  style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
                >
                  {areaLabel(area)}
                </div>
              ))}
              {csuCampusesBySelectivity.map((campus) => (
                <div key={campus} className="contents">
                  <div className="sticky left-0 z-10 flex items-center justify-end whitespace-nowrap bg-white pr-2 text-xs text-gray-600">
                    {campusName(campus)}
                  </div>
                  {csuMatrixAreas.map((area) => (
                    <HeatCell key={`${campus}|${area}`} campus={campus} area={area} level={level} />
                  ))}
                </div>
              ))}
            </div>
          </div>
        </Panel>

        <Panel
          title="Hardest programs in the system"
          note={`First-time freshmen, Fall ${CSU_DISCIPLINE_FALL}. Programs with at least 250 applicants.`}
        >
          <ol className="flex flex-col">
            {csuData.mostSelective.slice(0, 14).map((p, i) => (
              <li
                key={`${p.campus}|${p.major}`}
                className="grid items-center gap-2.5 border-b border-gray-100 py-2 last:border-b-0"
                style={{ gridTemplateColumns: "1.6rem 1fr 3rem" }}
              >
                <span className="text-right text-[11px] tabular-nums text-gray-400">{i + 1}</span>
                <span className="min-w-0">
                  <span className="block text-xs font-medium leading-snug text-gray-800">{p.major}</span>
                  <span className="block text-[11px] text-gray-400">
                    {campusName(p.campus)} · {fmtNum(p.applied)} applicants
                  </span>
                </span>
                <span className="text-right text-sm font-semibold tabular-nums" style={{ color: "#08465A" }}>
                  {fmtPct(p.admitRate)}
                </span>
              </li>
            ))}
          </ol>
        </Panel>
      </div>

      <Panel
        title="Largest programs by applications"
        aside={<RampKey ramp={BAR_RAMP} />}
        footnote={`First-time freshmen, Fall ${CSU_DISCIPLINE_FALL}. Bar length is applications received; colour is the admit rate, so a long dark bar is a program that is both popular and hard to enter.`}
      >
        <BarList rows={largest} labelWidth="17rem" />
      </Panel>
    </div>
  );
}

// ---------------------------------------------------------------------------
// California pipeline
// ---------------------------------------------------------------------------

function PipelineView() {
  const latest = csuStatewideLatest;
  const earliest = csuStatewideEarliest;
  const rate = latest.rate ?? 0;

  const points: ScatterPoint[] = useMemo(() => {
    // Only the four largest counties are labelled. Beyond that the labels
    // collide in the dense middle of the cloud, and every dot has a tooltip.
    const biggest = new Set(
      [...csuData.counties].sort((a, b) => b.graduates - a.graduates).slice(0, 4).map((c) => c.name)
    );
    return csuData.counties.map((c) => ({
      key: c.name,
      x: c.graduates,
      y: c.rate,
      size: c.graduates,
      labelled: biggest.has(c.name),
      tooltip: {
        title: `${c.name} County`,
        rows: [
          { label: "Graduates", value: fmtNum(c.graduates) },
          { label: "Met requirements", value: fmtNum(c.met) },
          { label: `Rate ${latest.year}`, value: fmtPct(c.rate) },
          { label: `Rate ${earliest.year}`, value: fmtPct(c.priorRate) },
        ],
      },
    }));
  }, [earliest.year, latest.year]);

  const countyRows = (counties: typeof csuCountiesByRate): BarRow[] =>
    counties.map((c) => ({
      key: c.name,
      label: `${c.name} County`,
      value: c.rate,
      display: fmtPct(c.rate),
      fill: c.rate < rate ? POPPY : TEAL,
      emphasis: c.rate < rate,
      tooltip: {
        title: `${c.name} County`,
        rows: [
          { label: "Graduates", value: fmtNum(c.graduates) },
          { label: "Met requirements", value: fmtNum(c.met) },
          { label: `Rate ${latest.year}`, value: fmtPct(c.rate) },
          { label: `Rate ${earliest.year}`, value: fmtPct(c.priorRate) },
        ],
      },
    }));

  const total = csuCountiesByRate.length;

  return (
    <div className="flex flex-col gap-4">
      <StatTiles
        tiles={[
          {
            label: "Met CSU requirements",
            value: fmtPct(rate),
            detail: `of California public high school graduates, ${latest.year}`,
          },
          {
            label: "Eligible graduates",
            value: fmtNum(latest.met),
            detail: `of ${fmtNum(latest.graduates)} total graduates`,
          },
          {
            label: `Change since ${earliest.year}`,
            value: <Delta value={rate - (earliest.rate ?? 0)} suffix=" pts" />,
            detail: `Up from ${fmtPct(earliest.rate)} in ${earliest.year}`,
          },
        ]}
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel
          title="Statewide a‑g completion"
          note="Share of public high school graduates completing the CSU and UC subject requirements"
        >
          <LineChart
            points={csuData.statewide.map((s) => ({ key: s.year.slice(2), value: s.rate ?? 0 }))}
            formatValue={(n) => `${n.toFixed(0)}%`}
            label="Statewide a-g completion by academic year"
          />
        </Panel>

        <Panel
          title="Every county"
          aside={
            <Legend
              items={[
                { label: "At or above statewide", color: TEAL },
                { label: "Below statewide", color: POPPY },
              ]}
            />
          }
          footnote="Dot size is the size of the graduating class; the horizontal axis is on a log scale so the small rural counties stay readable beside Los Angeles."
        >
          <Scatter
            points={points}
            xLabel={`High school graduates (${latest.year})`}
            yLabel="Met CSU requirements"
            refY={rate}
            refLabel={`Statewide ${fmtPct(rate)}`}
          />
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel
          title="Highest a‑g completion"
          note={`Top 12 of ${total} counties reporting, ${latest.year}`}
          footnote={`Orange marks a county below the statewide ${fmtPct(rate)}.`}
        >
          <BarList rows={countyRows(csuCountiesByRate.slice(0, 12))} max={75} labelWidth="9.5rem" />
        </Panel>
        <Panel
          title="Lowest a‑g completion"
          note={`Bottom 12 of ${total} counties reporting, ${latest.year}`}
          footnote={`Orange marks a county below the statewide ${fmtPct(rate)}.`}
        >
          <BarList
            rows={countyRows([...csuCountiesByRate.slice(-12)].reverse())}
            max={75}
            labelWidth="9.5rem"
          />
        </Panel>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function CSUPageClient() {
  const [tab, setTab] = useState<TabId>("system");

  const majorCount = useMemo(
    () => new Set(csuData.largest.concat(csuData.mostSelective).map((p) => p.major)).size,
    []
  );

  return (
    <TooltipProvider>
      <div className="min-h-screen pb-16">
        <div className="border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-6xl px-4 pt-6">
            <div className="flex flex-wrap items-baseline gap-3">
              <span className="h-5 w-2 rounded-sm" style={{ backgroundColor: POPPY }} />
              <h1 className="text-xl font-bold text-gray-900">CSU Explorer</h1>
              <p className="text-xs text-gray-400">
                Fall {CSU_EARLIEST_FALL}–{CSU_LATEST_FALL} admissions ·{" "}
                {csuCampusesBySelectivity.length} campuses · {csuAreasByVolume.length} discipline areas
              </p>
            </div>
            <nav className="mt-3 flex gap-0.5 overflow-x-auto" role="tablist" aria-label="CSU dashboards">
              {TABS.map((item) => {
                const active = item.id === tab;
                return (
                  <button
                    key={item.id}
                    type="button"
                    role="tab"
                    aria-selected={active}
                    onClick={() => setTab(item.id)}
                    className={`whitespace-nowrap border-b-2 px-3.5 py-2.5 text-sm font-semibold transition-colors ${
                      active
                        ? "text-gray-900"
                        : "border-transparent text-gray-400 hover:text-gray-700"
                    }`}
                    style={active ? { borderBottomColor: POPPY } : undefined}
                  >
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        <div className="mx-auto max-w-6xl px-4 py-5">
          {tab === "system" && <SystemwideView />}
          {tab === "campus" && <CampusView />}
          {tab === "matrix" && <MatrixView />}
          {tab === "pipeline" && <PipelineView />}
        </div>

        <div className="mx-auto max-w-6xl px-4 text-xs leading-relaxed text-gray-400">
          <p className="mb-2">
            <strong className="font-semibold text-gray-500">Source</strong> — CSU Institutional
            Research data dashboards. Admissions counts are Fall term. Discipline figures cover
            first-time freshmen and undergraduate transfers across {majorCount}+ majors; campus
            totals cover all entry levels, so they are larger than the discipline sums.
          </p>
          <p>
            <strong className="font-semibold text-gray-500">Gaps carried from the source</strong> —
            the CSU suppresses enrollment in much of Fall {CSU_EARLIEST_FALL} and Fall{" "}
            {CSU_EARLIEST_FALL + 1} at the discipline level, so discipline views report Fall{" "}
            {CSU_DISCIPLINE_FALL} only rather than a trend that would show a reporting gap as a
            collapse. Nothing here is estimated or interpolated. Cal Maritime is reported separately
            through Fall {CSU_LATEST_FALL} and is kept separate here.
          </p>
        </div>
      </div>
    </TooltipProvider>
  );
}
