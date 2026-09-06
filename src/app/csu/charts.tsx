"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

// ---------------------------------------------------------------------------
// Palette
//
// Admit rate is a magnitude, so it is carried by a single-hue sequential ramp
// where dark means selective. Two ramps exist because the two places colour is
// used have different floors: a heatmap cell carries a number and can go very
// pale, while a bar sits on a white card and cannot.
//
// The categorical pair (teal / poppy) was checked for colour-vision separation
// and contrast before use.
// ---------------------------------------------------------------------------

export const TEAL = "#0A84A8";
export const TEAL_DEEP = "#08465A";
export const POPPY = "#DD4B21";

export const HEAT_RAMP = [
  "#DFEEF3",
  "#C2E0E9",
  "#9FD0DE",
  "#74B8CD",
  "#4BA0BB",
  "#1B85A6",
  "#0E6584",
  "#08465A",
];

export const BAR_RAMP = ["#8FC5D5", "#5FADC5", "#3492B1", "#12789B", "#0A5C79", "#08465A"];

// Stops track where CSU admit rates actually sit — a long tail below 60 and a
// dense cluster above 80 — so the ramp spends its range on the data.
const HEAT_STOPS = [20, 35, 50, 62, 72, 80, 88];
const BAR_STOPS = [30, 50, 65, 78, 88];

function step(ramp: string[], stops: number[], rate: number | null): string {
  if (rate == null) return ramp[0];
  let i = 0;
  while (i < stops.length && rate > stops[i]) i += 1;
  return ramp[ramp.length - 1 - i];
}

/** Heatmap cell fill for an admit rate. Dark means selective. */
export const heatFill = (rate: number | null) => step(HEAT_RAMP, HEAT_STOPS, rate);

/** Bar fill for an admit rate, floored at a step that reads on white. */
export const barFill = (rate: number | null) => step(BAR_RAMP, BAR_STOPS, rate);

/** Ink that stays legible on a heatmap cell. */
export function inkOn(fill: string): string {
  const i = HEAT_RAMP.indexOf(fill);
  return i >= 0 && i <= 3 ? "#1a1a1a" : "#ffffff";
}

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

export function fmtNum(n: number | null | undefined): string {
  if (n == null) return "—";
  return new Intl.NumberFormat("en-US").format(n);
}

export function fmtPct(n: number | null | undefined, decimals = 1): string {
  if (n == null) return "—";
  return `${n.toFixed(decimals)}%`;
}

export function fmtCompact(n: number): string {
  return n >= 1000 ? `${Math.round(n / 1000)}k` : `${Math.round(n)}`;
}

// ---------------------------------------------------------------------------
// Tooltip
//
// One fixed-position node for the whole page. Charts call show/move/hide rather
// than each rendering its own.
// ---------------------------------------------------------------------------

export interface TooltipRow {
  label: string;
  value: string;
}

interface TooltipContent {
  title: string;
  rows: TooltipRow[];
}

interface TooltipApi {
  show: (content: TooltipContent, e: { clientX: number; clientY: number }) => void;
  move: (e: { clientX: number; clientY: number }) => void;
  hide: () => void;
}

const noop: TooltipApi = { show: () => {}, move: () => {}, hide: () => {} };
const TooltipContext = createContext<TooltipApi>(noop);

export const useTooltip = () => useContext(TooltipContext);

/**
 * Returns the mouse handlers a hoverable mark needs. Pass `null` for marks that
 * have nothing to say.
 */
export function useHover(content: TooltipContent | null) {
  const tip = useTooltip();
  return useMemo(() => {
    if (!content) return {};
    return {
      onMouseEnter: (e: React.MouseEvent) => tip.show(content, e),
      onMouseMove: (e: React.MouseEvent) => tip.move(e),
      onMouseLeave: () => tip.hide(),
    };
  }, [content, tip]);
}

export function TooltipProvider({ children }: { children: ReactNode }) {
  const [content, setContent] = useState<TooltipContent | null>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });

  const place = useCallback((e: { clientX: number; clientY: number }) => {
    setPos({ x: e.clientX, y: e.clientY });
  }, []);

  const api = useMemo<TooltipApi>(
    () => ({
      show: (next, e) => {
        setContent(next);
        place(e);
      },
      move: place,
      hide: () => setContent(null),
    }),
    [place]
  );

  // Flip the tooltip toward whichever side has room.
  const width = 250;
  const height = 32 + (content?.rows.length ?? 0) * 20;
  const flipX = typeof window !== "undefined" && pos.x + width + 24 > window.innerWidth;
  const flipY = typeof window !== "undefined" && pos.y + height + 26 > window.innerHeight;

  return (
    <TooltipContext.Provider value={api}>
      {children}
      {content && (
        <div
          role="status"
          aria-live="polite"
          className="pointer-events-none fixed z-50 rounded-md px-3 py-2 text-xs leading-relaxed shadow-xl"
          style={{
            left: flipX ? pos.x - width - 14 : pos.x + 14,
            top: flipY ? pos.y - height - 14 : pos.y + 16,
            width,
            backgroundColor: "#121A1F",
            color: "#ffffff",
          }}
        >
          <div className="mb-1 font-semibold">{content.title}</div>
          {content.rows.map((row) => (
            <div key={row.label} className="flex justify-between gap-4">
              <span style={{ color: "#C6D3DA" }}>{row.label}</span>
              <span className="tabular-nums">{row.value}</span>
            </div>
          ))}
        </div>
      )}
    </TooltipContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// Layout pieces
// ---------------------------------------------------------------------------

export function Panel({
  title,
  note,
  aside,
  children,
  footnote,
}: {
  title: string;
  note?: string;
  aside?: ReactNode;
  children: ReactNode;
  footnote?: string;
}) {
  return (
    <section className="card p-5">
      <header className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <h2 className="text-sm font-semibold text-gray-800">{title}</h2>
        {aside ?? (note && <p className="max-w-sm text-right text-xs text-gray-400">{note}</p>)}
      </header>
      {children}
      {footnote && (
        <p className="mt-3 border-t border-gray-100 pt-3 text-xs text-gray-400">{footnote}</p>
      )}
    </section>
  );
}

export function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
      {items.map((item) => (
        <span key={item.label} className="flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-sm"
            style={{ backgroundColor: item.color }}
          />
          {item.label}
        </span>
      ))}
    </div>
  );
}

export function RampKey({ ramp = HEAT_RAMP }: { ramp?: string[] }) {
  return (
    <div className="flex items-center gap-2 text-xs text-gray-400">
      <span>More selective</span>
      <span className="flex">
        {[...ramp].reverse().map((color) => (
          <span key={color} className="h-2.5 w-5" style={{ backgroundColor: color }} />
        ))}
      </span>
      <span>Less selective</span>
    </div>
  );
}

export function StatTiles({
  tiles,
}: {
  tiles: { label: string; value: ReactNode; detail: ReactNode }[];
}) {
  // Pick the column count the tiles actually fill, so a three-tile row does not
  // leave a dead fourth column.
  const columns = tiles.length === 3 ? "lg:grid-cols-3" : "lg:grid-cols-4";
  return (
    <div className={`card grid grid-cols-2 overflow-hidden ${columns}`}>
      {tiles.map((tile, i) => (
        <div
          key={tile.label}
          className={`flex min-w-0 flex-col gap-1 p-4 sm:p-5 ${
            i < tiles.length - 1 ? "border-b border-gray-100 lg:border-b-0 lg:border-r" : ""
          }`}
        >
          <div className="text-[10px] font-semibold uppercase tracking-widest text-gray-400">
            {tile.label}
          </div>
          <div className="text-2xl font-bold tabular-nums text-gray-800 sm:text-3xl">
            {tile.value}
          </div>
          <div className="text-xs text-gray-500">{tile.detail}</div>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Bar list
// ---------------------------------------------------------------------------

export interface BarRow {
  key: string;
  label: string;
  value: number;
  fill: string;
  display: string;
  emphasis?: boolean;
  tooltip?: TooltipContent;
}

function Bar({ row, max, labelWidth }: { row: BarRow; max: number; labelWidth: string }) {
  const hover = useHover(row.tooltip ?? null);
  return (
    <div
      className="-mx-1.5 grid items-center gap-3 rounded px-1.5 py-0.5 hover:bg-gray-50"
      style={{ gridTemplateColumns: `${labelWidth} 1fr 3.4rem` }}
      {...hover}
    >
      <div
        className={`truncate text-xs ${
          row.emphasis ? "font-semibold text-gray-800" : "text-gray-600"
        }`}
        title={row.label}
      >
        {row.label}
      </div>
      <div className="h-3.5 rounded-sm bg-gray-100">
        <div
          className="h-full rounded-sm"
          style={{
            width: `${Math.max(0, Math.min(100, (row.value / max) * 100))}%`,
            minWidth: 2,
            backgroundColor: row.fill,
          }}
        />
      </div>
      <div className="text-right text-xs tabular-nums text-gray-700">{row.display}</div>
    </div>
  );
}

export function BarList({
  rows,
  max,
  labelWidth = "9rem",
}: {
  rows: BarRow[];
  max?: number;
  labelWidth?: string;
}) {
  const ceiling = max ?? Math.max(...rows.map((r) => r.value), 1);
  return (
    <div className="flex flex-col gap-0.5">
      {rows.map((row) => (
        <Bar key={row.key} row={row} max={ceiling} labelWidth={labelWidth} />
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Line chart
// ---------------------------------------------------------------------------

export function LineChart({
  points,
  color = TEAL,
  formatValue,
  label,
  height = 170,
}: {
  points: { key: string; value: number }[];
  color?: string;
  formatValue: (n: number) => string;
  label: string;
  height?: number;
}) {
  const width = 430;
  const pad = { top: 16, right: 18, bottom: 26, left: 46 };
  const iw = width - pad.left - pad.right;
  const ih = height - pad.top - pad.bottom;

  const values = points.map((p) => p.value);
  let lo = Math.min(...values);
  let hi = Math.max(...values);
  if (hi === lo) hi = lo + 1;
  const span = hi - lo;
  lo -= span * 0.18;
  hi += span * 0.18;

  const x = (i: number) => pad.left + (points.length === 1 ? iw / 2 : (i / (points.length - 1)) * iw);
  const y = (v: number) => pad.top + ih - ((v - lo) / (hi - lo)) * ih;

  const ticks = [lo + (hi - lo) * 0.08, lo + (hi - lo) * 0.5, hi - (hi - lo) * 0.08];
  const path = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const last = points[points.length - 1];

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label={label}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={pad.left} x2={width - pad.right} y1={y(t)} y2={y(t)} stroke="#f1f3f5" strokeWidth={1} />
          <text x={pad.left - 7} y={y(t) + 3.5} textAnchor="end" fontSize={10} fill="#9ca3af" className="tabular-nums">
            {formatValue(t)}
          </text>
        </g>
      ))}
      <path d={`${path} L${x(points.length - 1).toFixed(1)},${pad.top + ih} L${x(0).toFixed(1)},${pad.top + ih} Z`} fill={color} fillOpacity={0.1} />
      <path d={path} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      {points.map((p, i) => (
        <g key={p.key}>
          <circle
            cx={x(i)}
            cy={y(p.value)}
            r={i === points.length - 1 ? 5 : 4}
            fill={i === points.length - 1 ? POPPY : color}
            stroke="#ffffff"
            strokeWidth={2}
          >
            <title>{`${p.key}: ${formatValue(p.value)}`}</title>
          </circle>
          <text x={x(i)} y={height - 8} textAnchor="middle" fontSize={10} fill="#9ca3af">
            {p.key}
          </text>
        </g>
      ))}
      <text
        x={x(points.length - 1)}
        y={y(last.value) - 12}
        textAnchor="end"
        fontSize={12.5}
        fontWeight={600}
        fill={POPPY}
        className="tabular-nums"
      >
        {formatValue(last.value)}
      </text>
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Grouped bars
// ---------------------------------------------------------------------------

export function GroupedBars({
  groups,
  series,
  formatValue,
  label,
  height = 210,
}: {
  groups: { key: string; values: Record<string, number | null> }[];
  series: { key: string; name: string; color: string }[];
  formatValue: (n: number) => string;
  label: string;
  height?: number;
}) {
  const width = 470;
  const pad = { top: 16, right: 12, bottom: 30, left: 52 };
  const iw = width - pad.left - pad.right;
  const ih = height - pad.top - pad.bottom;

  const peak = Math.max(...groups.flatMap((g) => series.map((s) => g.values[s.key] ?? 0)), 1) * 1.08;
  const groupWidth = iw / groups.length;
  const barWidth = Math.min(20, (groupWidth - 12) / series.length);
  const y = (v: number) => pad.top + ih - (v / peak) * ih;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label={label}>
      {[0, 0.25, 0.5, 0.75, 1].map((f) => (
        <g key={f}>
          <line x1={pad.left} x2={width - pad.right} y1={y(peak * f)} y2={y(peak * f)} stroke="#f1f3f5" strokeWidth={1} />
          <text x={pad.left - 7} y={y(peak * f) + 3.5} textAnchor="end" fontSize={10} fill="#9ca3af" className="tabular-nums">
            {formatValue(peak * f)}
          </text>
        </g>
      ))}
      {groups.map((group, gi) => {
        const center = pad.left + groupWidth * gi + groupWidth / 2;
        const start = center - (barWidth * series.length + 2 * (series.length - 1)) / 2;
        return (
          <g key={group.key}>
            {series.map((s, si) => {
              const value = group.values[s.key] ?? 0;
              const top = y(value);
              return (
                <rect
                  key={s.key}
                  x={start + si * (barWidth + 2)}
                  y={top}
                  width={barWidth}
                  height={Math.max(1, pad.top + ih - top)}
                  rx={3}
                  fill={s.color}
                >
                  <title>{`${group.key} · ${s.name}: ${fmtNum(group.values[s.key])}`}</title>
                </rect>
              );
            })}
            <text x={center} y={height - 9} textAnchor="middle" fontSize={10} fill="#9ca3af">
              {group.key}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Scatter
// ---------------------------------------------------------------------------

export interface ScatterPoint {
  key: string;
  x: number;
  y: number;
  size: number;
  labelled?: boolean;
  tooltip?: TooltipContent;
}

function Dot({ point, cx, cy, r, fill }: { point: ScatterPoint; cx: number; cy: number; r: number; fill: string }) {
  const hover = useHover(point.tooltip ?? null);
  return (
    <circle
      cx={cx}
      cy={cy}
      r={r}
      fill={fill}
      fillOpacity={0.72}
      stroke="#ffffff"
      strokeWidth={1.5}
      className="hover:stroke-2"
      {...hover}
    >
      <title>{point.key}</title>
    </circle>
  );
}

export function Scatter({
  points,
  xLabel,
  yLabel,
  refY,
  refLabel,
  height = 330,
}: {
  points: ScatterPoint[];
  xLabel: string;
  yLabel: string;
  refY?: number;
  refLabel?: string;
  height?: number;
}) {
  const width = 560;
  const pad = { top: 16, right: 18, bottom: 42, left: 48 };
  const iw = width - pad.left - pad.right;
  const ih = height - pad.top - pad.bottom;

  const xLo = Math.log10(Math.max(60, Math.min(...points.map((p) => p.x))) * 0.75);
  const xHi = Math.log10(Math.max(...points.map((p) => p.x)) * 1.35);
  const yLo = Math.max(0, Math.min(...points.map((p) => p.y)) - 6);
  const yHi = Math.min(100, Math.max(...points.map((p) => p.y)) + 6);

  const x = (v: number) => pad.left + ((Math.log10(v) - xLo) / (xHi - xLo)) * iw;
  const y = (v: number) => pad.top + ih - ((v - yLo) / (yHi - yLo)) * ih;
  const maxSize = Math.max(...points.map((p) => p.size), 1);
  const radius = (p: ScatterPoint) => 4 + Math.sqrt(p.size / maxSize) * 13;

  const yTicks = [20, 30, 40, 50, 60, 70].filter((t) => t >= yLo && t <= yHi);
  const xTicks = [100, 1000, 10000, 50000].filter((v) => Math.log10(v) >= xLo && Math.log10(v) <= xHi);
  const drawOrder = [...points].sort((a, b) => b.size - a.size);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label={`${yLabel} against ${xLabel}`}>
      {yTicks.map((t) => (
        <g key={`y${t}`}>
          <line x1={pad.left} x2={width - pad.right} y1={y(t)} y2={y(t)} stroke="#f1f3f5" strokeWidth={1} />
          <text x={pad.left - 7} y={y(t) + 3.5} textAnchor="end" fontSize={10} fill="#9ca3af">{`${t}%`}</text>
        </g>
      ))}
      {xTicks.map((v) => (
        <g key={`x${v}`}>
          <line x1={x(v)} x2={x(v)} y1={pad.top} y2={pad.top + ih} stroke="#f1f3f5" strokeWidth={1} />
          <text x={x(v)} y={height - 24} textAnchor="middle" fontSize={10} fill="#9ca3af">
            {v >= 1000 ? `${v / 1000}k` : v}
          </text>
        </g>
      ))}
      {refY != null && (
        <g>
          <line x1={pad.left} x2={width - pad.right} y1={y(refY)} y2={y(refY)} stroke={POPPY} strokeWidth={1.5} strokeDasharray="5 4" />
          <text x={width - pad.right} y={y(refY) - 7} textAnchor="end" fontSize={10.5} fontWeight={600} fill={POPPY}>
            {refLabel}
          </text>
        </g>
      )}
      {drawOrder.map((p) => (
        <Dot
          key={p.key}
          point={p}
          cx={x(p.x)}
          cy={y(p.y)}
          r={radius(p)}
          fill={refY != null && p.y < refY ? POPPY : TEAL}
        />
      ))}
      {points
        .filter((p) => p.labelled)
        .map((p) => (
          <text
            key={`l${p.key}`}
            x={x(p.x)}
            y={y(p.y) - radius(p) - 5}
            textAnchor="middle"
            fontSize={10.5}
            fontWeight={600}
            fill="#4b5563"
          >
            {p.key}
          </text>
        ))}
      <text x={pad.left + iw / 2} y={height - 5} textAnchor="middle" fontSize={10} fontWeight={600} fill="#9ca3af" letterSpacing="0.08em">
        {xLabel.toUpperCase()}
      </text>
      <text x={-(pad.top + ih / 2)} y={12} transform="rotate(-90)" textAnchor="middle" fontSize={10} fontWeight={600} fill="#9ca3af" letterSpacing="0.08em">
        {yLabel.toUpperCase()}
      </text>
    </svg>
  );
}
