"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

export interface HeroPoint {
  year: number;
  rate: number;
}

export interface HeroSeries {
  slug: string;
  name: string;
  color: string;
  points: HeroPoint[];
}

interface HeroTrendChartProps {
  series: HeroSeries[];
}

const W = 880;
const H = 380;
const PAD = { top: 28, right: 128, bottom: 42, left: 52 };

function smoothPath(pts: { x: number; y: number }[]): string {
  if (pts.length < 2) return "";
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[Math.min(pts.length - 1, i + 2)];
    const c1x = p1.x + (p2.x - p0.x) / 6;
    const c1y = p1.y + (p2.y - p0.y) / 6;
    const c2x = p2.x - (p3.x - p1.x) / 6;
    const c2y = p2.y - (p3.y - p1.y) / 6;
    d += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)}, ${c2x.toFixed(1)} ${c2y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
  }
  return d;
}

export default function HeroTrendChart({ series }: HeroTrendChartProps) {
  const router = useRouter();
  const [active, setActive] = useState<string | null>(null);

  const chart = useMemo(() => {
    const allPoints = series.flatMap((s) => s.points);
    const minYear = Math.min(...allPoints.map((p) => p.year));
    const maxYear = Math.max(...allPoints.map((p) => p.year));
    const maxRate = Math.max(...allPoints.map((p) => p.rate));
    const yMax = Math.ceil((maxRate * 100) / 10) / 10; // e.g. 0.289 -> 0.3

    const x = (year: number) =>
      PAD.left + ((year - minYear) / (maxYear - minYear)) * (W - PAD.left - PAD.right);
    const y = (rate: number) =>
      PAD.top + (1 - rate / yMax) * (H - PAD.top - PAD.bottom);

    const lines = series.map((s) => {
      const pts = s.points.map((p) => ({ x: x(p.year), y: y(p.rate) }));
      const last = s.points[s.points.length - 1];
      return {
        slug: s.slug,
        name: s.name,
        color: s.color,
        path: smoothPath(pts),
        end: { x: x(last.year), y: y(last.rate) },
        lastRate: last.rate,
      };
    });

    // Nudge end labels apart so they never overlap
    const MIN_GAP = 19;
    const labels = lines
      .map((l) => ({ slug: l.slug, y: l.end.y }))
      .sort((a, b) => a.y - b.y);
    for (let i = 1; i < labels.length; i++) {
      if (labels[i].y - labels[i - 1].y < MIN_GAP) {
        labels[i].y = labels[i - 1].y + MIN_GAP;
      }
    }
    const labelY = Object.fromEntries(labels.map((l) => [l.slug, l.y]));

    const yTicks = [];
    for (let r = 0.1; r <= yMax + 1e-9; r += 0.1) yTicks.push(r);

    const xTicks = [];
    for (let yr = minYear; yr <= maxYear; yr += 2) xTicks.push(yr);

    return { lines, labelY, yTicks, xTicks, x, y, minYear, maxYear };
  }, [series]);

  const isDimmed = (slug: string) => active !== null && active !== slug;

  return (
    <div
      className="relative hero-rise mx-auto w-full text-left"
      style={{ animationDelay: "0.3s" }}
    >
      {/* Glow behind the window */}
      <div
        aria-hidden
        className="absolute -inset-x-10 -inset-y-12 pointer-events-none"
        style={{
          background:
            "radial-gradient(45% 55% at 30% 40%, rgba(94, 106, 210, 0.14) 0%, transparent 70%), radial-gradient(40% 50% at 75% 55%, rgba(174, 102, 240, 0.10) 0%, transparent 70%)",
        }}
      />

      {/* Product window */}
      <div
        className="relative rounded-2xl overflow-hidden"
        style={{
          border: "1px solid rgba(0, 0, 0, 0.08)",
          background: "linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%)",
          boxShadow:
            "0 0 0 1px rgba(0,0,0,0.03), 0 32px 80px -24px rgba(23, 26, 43, 0.22)",
        }}
      >
        {/* Title bar */}
        <div
          className="flex items-center gap-3 px-4 sm:px-5 py-3"
          style={{ borderBottom: "1px solid rgba(0, 0, 0, 0.06)" }}
        >
          <div className="flex items-center gap-1.5" aria-hidden>
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: "#ff5f57" }} />
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: "#febc2e" }} />
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: "#28c840" }} />
          </div>
          <span className="text-xs sm:text-sm font-medium" style={{ color: "#3a3d43" }}>
            Acceptance rate, {chart.minYear}–{chart.maxYear + 1}
          </span>
          <span className="ml-auto hidden sm:block text-xs" style={{ color: "#62666d" }}>
            Source: official Common Data Sets
          </span>
        </div>

        {/* School chips */}
        <div className="flex flex-wrap items-center gap-2 px-4 sm:px-5 pt-4">
          {series.map((s) => {
            const last = s.points[s.points.length - 1];
            return (
              <button
                key={s.slug}
                onMouseEnter={() => setActive(s.slug)}
                onMouseLeave={() => setActive(null)}
                onFocus={() => setActive(s.slug)}
                onBlur={() => setActive(null)}
                onClick={() => router.push(`/${s.slug}`)}
                className="flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium transition-colors cursor-pointer"
                style={{
                  border: `1px solid ${active === s.slug ? "rgba(0,0,0,0.22)" : "rgba(0,0,0,0.1)"}`,
                  color: isDimmed(s.slug) ? "#9096a0" : "#1a1a1a",
                  background: active === s.slug ? "rgba(0,0,0,0.04)" : "transparent",
                }}
                title={`Open ${s.name} dashboard`}
              >
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ background: s.color, opacity: isDimmed(s.slug) ? 0.35 : 1 }}
                  aria-hidden
                />
                {s.name}
                <span style={{ color: "#62666d" }} className="tabular-nums">
                  {(last.rate * 100).toFixed(1)}%
                </span>
              </button>
            );
          })}
        </div>

        {/* Chart */}
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full h-auto block"
          role="img"
          aria-label="Line chart of acceptance rates over time for five universities"
        >
          {/* Gridlines + y labels */}
          {chart.yTicks.map((r) => (
            <g key={r}>
              <line
                x1={PAD.left}
                x2={W - PAD.right}
                y1={chart.y(r)}
                y2={chart.y(r)}
                stroke="rgba(0,0,0,0.06)"
              />
              <text
                x={PAD.left - 10}
                y={chart.y(r) + 4}
                textAnchor="end"
                fontSize="11"
                fill="#5c626b"
              >
                {Math.round(r * 100)}%
              </text>
            </g>
          ))}
          {/* Baseline */}
          <line
            x1={PAD.left}
            x2={W - PAD.right}
            y1={chart.y(0)}
            y2={chart.y(0)}
            stroke="rgba(0,0,0,0.14)"
          />
          {/* X labels */}
          {chart.xTicks.map((yr) => (
            <text
              key={yr}
              x={chart.x(yr)}
              y={H - PAD.bottom + 24}
              textAnchor="middle"
              fontSize="11"
              fill="#5c626b"
            >
              {yr}
            </text>
          ))}

          {/* Series */}
          {chart.lines.map((line, i) => (
            <g
              key={line.slug}
              style={{
                opacity: isDimmed(line.slug) ? 0.14 : 1,
                transition: "opacity 0.25s ease",
              }}
            >
              <path
                d={line.path}
                fill="none"
                stroke={line.color}
                strokeWidth={active === line.slug ? 3.2 : 2.4}
                strokeLinecap="round"
                pathLength={1}
                className="hero-line"
                style={{
                  animationDelay: `${0.5 + i * 0.18}s`,
                  filter:
                    active === line.slug
                      ? `drop-shadow(0 0 7px ${line.color})`
                      : undefined,
                  transition: "stroke-width 0.25s ease",
                }}
              />
              <g
                className="hero-fade"
                style={{ animationDelay: `${1.7 + i * 0.18}s` }}
              >
                <circle cx={line.end.x} cy={line.end.y} r={4} fill={line.color} />
                <text
                  x={line.end.x + 12}
                  y={chart.labelY[line.slug] + 4}
                  fontSize="12"
                  fontWeight="600"
                  fill={line.color}
                >
                  {line.name}
                  <tspan fill="#8a8f98" fontWeight="400">
                    {" "}
                    {(line.lastRate * 100).toFixed(1)}%
                  </tspan>
                </text>
              </g>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}
