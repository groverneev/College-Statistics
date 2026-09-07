"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import useMediaQuery from "@/components/useMediaQuery";
import {
  chartRows,
  changeChartRows,
  annualMedianRows,
  baseYear,
  factBullets,
  lede,
  metrics,
  reportYear,
  sourceLinks,
  sourceNote,
} from "@/data/trends/international-enrollment/data";

const BLUE = "#1D4F91";
const RED = "#B3322A";

function formatPercent(value: number | string | undefined) {
  return typeof value === "number" ? `${value.toFixed(1)}%` : "";
}

function formatNumber(value: number) {
  return value.toLocaleString("en-US");
}

function InternationalShareChart() {
  const isDesktop = useMediaQuery("(min-width: 640px)");
  const data = chartRows.map((row) => ({
    school: row.shortName,
    share: Number(row.share.toFixed(1)),
    international: row.international,
    undergraduate: row.undergraduate,
  }));

  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        {metrics.schoolsAtLeastTenPercent} of {metrics.reportSchoolCount} Schools Reported Double-Digit International Enrollment
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        {reportYear} · 15 highest shares shown; international undergraduates as a share of all undergraduates
      </p>

      {isDesktop ? (
        <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={410}>
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 4, right: 34, left: 92, bottom: 4 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, "dataMax + 3"]}
              tickFormatter={(value) => `${value}%`}
              tick={{ fontSize: 12 }}
            />
            <YAxis type="category" dataKey="school" tick={{ fontSize: 12 }} width={118} />
            <Tooltip
              formatter={(value, _name, item) => {
                const payload = item?.payload as (typeof data)[number] | undefined;
                return [
                  `${formatPercent(value as number)} (${formatNumber(payload?.international ?? 0)} students)`,
                  "Share",
                ];
              }}
            />
            <Bar dataKey="share" name="International share" radius={[0, 3, 3, 0]}>
              {data.map((entry, index) => (
                <Cell key={entry.school} fill={index < 4 ? BLUE : "#6B7280"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="space-y-3">
          {data.map((row, index) => (
            <div key={row.school}>
              <div className="mb-1 flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-gray-700">{row.school}</span>
                <span className="font-semibold tabular-nums text-gray-800">
                  {formatPercent(row.share)}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${(row.share / data[0].share) * 100}%`,
                    backgroundColor: index < 4 ? BLUE : "#6B7280",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-3">
        Share is calculated as CDS-reported international undergraduates divided by total undergraduate enrollment.
      </p>
    </div>
  );
}

function MedianShareTrendChart() {
  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        Median Share Rose from {metrics.medianBaseShare.toFixed(1)}% to {metrics.medianReportShare.toFixed(1)}%
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        {baseYear} to {reportYear} · median across the same {metrics.comparisonSchoolCount}-school panel
      </p>
      <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={280}>
        <LineChart data={annualMedianRows} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis
            domain={[9, 12]}
            tickFormatter={(value) => `${value}%`}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value, _name, item) => [
              `${Number(value).toFixed(1)}% (n=${item?.payload?.schoolCount ?? "—"})`,
              "Median share",
            ]}
          />
          <ReferenceLine y={10} stroke="#9CA3AF" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="share"
            name="Median share"
            stroke={BLUE}
            strokeWidth={3}
            dot={{ r: 3, fill: BLUE }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-3">
        The panel includes schools with data in both endpoint years; one school is missing in 2022–23.
      </p>
    </div>
  );
}

function ShareChangeChart() {
  const isDesktop = useMediaQuery("(min-width: 640px)");
  const data = changeChartRows.map((row) => ({
    school: row.shortName,
    change: Number(row.change.toFixed(1)),
    baseShare: row.baseShare,
    reportShare: row.reportShare,
  }));

  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">
        {metrics.schoolsUp} Schools Gained Share; {metrics.schoolsDown} Declined
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        {baseYear} → {reportYear} · selected schools shown · percentage-point change
      </p>

      {isDesktop ? (
        <ResponsiveContainer initialDimension={{ width: 1, height: 1 }} width="100%" height={330}>
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 4, right: 36, left: 92, bottom: 4 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
            <XAxis
              type="number"
              domain={["dataMin - 1", "dataMax + 1"]}
              tickFormatter={(value) => `${value} pp`}
              tick={{ fontSize: 12 }}
            />
            <YAxis type="category" dataKey="school" tick={{ fontSize: 12 }} width={118} />
            <Tooltip
              formatter={(value, _name, item) => {
                const payload = item?.payload as (typeof data)[number] | undefined;
                const numericValue = Number(value);
                return [
                  `${numericValue >= 0 ? "+" : ""}${numericValue.toFixed(1)} pp (${payload?.baseShare.toFixed(1)}% → ${payload?.reportShare.toFixed(1)}%)`,
                  "Change",
                ];
              }}
            />
            <ReferenceLine x={0} stroke="#9CA3AF" />
            <Bar dataKey="change" name="Change">
              {data.map((entry) => (
                <Cell key={entry.school} fill={entry.change >= 0 ? BLUE : RED} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="space-y-3">
          {data.map((row) => (
            <div key={row.school} className="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
              <div className="flex items-center justify-between gap-3">
                <span className="font-medium text-gray-700">{row.school}</span>
                <span className={`text-sm font-semibold tabular-nums ${row.change >= 0 ? "text-blue-700" : "text-red-600"}`}>
                  {row.change >= 0 ? "+" : ""}{row.change.toFixed(1)} pp
                </span>
              </div>
              <div className="mt-1 text-xs text-gray-400">
                {row.baseShare.toFixed(1)}% → {row.reportShare.toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-4">
        Positive examples are shown in blue; negative examples are shown in red. Changes are calculated from the same school’s undergraduate enrollment in each endpoint year.
      </p>
    </div>
  );
}

function Sources() {
  return (
    <div className="card p-4 sm:p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Sources and methodology</h3>
      <ul className="space-y-2">
        {sourceLinks.map((source) => (
          <li key={source.url} className="text-sm">
            <a href={source.url} className="text-blue-700 hover:underline">
              {source.label}
            </a>
          </li>
        ))}
      </ul>
      <p className="text-xs text-gray-400 mt-4">{sourceNote}</p>
    </div>
  );
}

export default function InternationalEnrollmentStory() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="card p-4 sm:p-6">
        <p className="text-gray-700 leading-relaxed text-base">{lede}</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5">
          {[
            { value: `${chartRows[0]?.share.toFixed(1)}%`, label: `${chartRows[0]?.school} international share` },
            { value: `${metrics.schoolsAtLeastTenPercent}/${metrics.reportSchoolCount}`, label: "schools at 10% or higher" },
            { value: `${metrics.schoolsDown}`, label: "schools down more than 0.5 pp" },
          ].map((stat) => (
            <div key={stat.label} className="rounded-lg bg-gray-50 px-4 py-3">
              <div className="text-2xl font-bold text-gray-900 tabular-nums">{stat.value}</div>
              <div className="mt-1 text-xs text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <InternationalShareChart />
      <MedianShareTrendChart />

      <div className="card p-4 sm:p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Key findings</h3>
        <ul className="space-y-3">
          {factBullets.map((fact) => (
            <li key={fact} className="flex items-start gap-3 text-gray-700 text-sm">
              <span className="mt-1 w-2 h-2 rounded-full bg-gray-800 flex-shrink-0" />
              {fact}
            </li>
          ))}
        </ul>
      </div>

      <ShareChangeChart />

      <Sources />
    </div>
  );
}
