"use client";

import { YearData } from "@/lib/types";
import { formatNumber } from "@/utils/dataHelpers";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface DemographicsTrendChartProps {
  yearData: Record<string, YearData>;
  schoolColor: string;
}

const RACE_COLORS: Record<string, string> = {
  white: "#95a5a6",
  asian: "#3498db",
  hispanicLatino: "#e67e22",
  blackAfricanAmerican: "#27ae60",
  international: "#9b59b6",
  twoOrMoreRaces: "#e74c3c",
};

const RACE_LABELS: Record<string, string> = {
  white: "White",
  asian: "Asian",
  hispanicLatino: "Hispanic/Latino",
  blackAfricanAmerican: "Black/African American",
  international: "International",
  twoOrMoreRaces: "Two or More",
};

export default function DemographicsTrendChart({
  yearData,
  schoolColor,
}: DemographicsTrendChartProps) {
  const years = Object.keys(yearData).sort();
  const yearsWithEnrollment = years.filter(
    (year) => yearData[year].demographics.enrollment.undergraduate > 0
  );
  const latestYear = yearsWithEnrollment[yearsWithEnrollment.length - 1] || years[years.length - 1];
  const latestDemo = yearData[latestYear].demographics;
  const totalUndergrad = latestDemo.enrollment.undergraduate;

  // Enrollment trend data
  const enrollmentData = yearsWithEnrollment.map((year) => ({
    year: year.split("-")[0],
    fullYear: year,
    undergraduate: yearData[year].demographics.enrollment.undergraduate,
    graduate: yearData[year].demographics.enrollment.graduate || 0,
  }));

  // Demographics trend data (percentages over time)
  const demographicsData = yearsWithEnrollment.map((year) => {
    const demo = yearData[year].demographics;
    const total = demo.enrollment.undergraduate;
    const hasDetailedRaceData =
      demo.byRace.white +
        demo.byRace.asian +
        demo.byRace.hispanicLatino +
        demo.byRace.blackAfricanAmerican +
        demo.byRace.international +
        demo.byRace.twoOrMoreRaces >
      0;

    return {
      year: year.split("-")[0],
      fullYear: year,
      white: total > 0 && hasDetailedRaceData ? (demo.byRace.white / total) * 100 : null,
      asian: total > 0 && hasDetailedRaceData ? (demo.byRace.asian / total) * 100 : null,
      hispanicLatino:
        total > 0 && hasDetailedRaceData ? (demo.byRace.hispanicLatino / total) * 100 : null,
      blackAfricanAmerican:
        total > 0 && hasDetailedRaceData ? (demo.byRace.blackAfricanAmerican / total) * 100 : null,
      international:
        total > 0 && hasDetailedRaceData ? (demo.byRace.international / total) * 100 : null,
      twoOrMoreRaces:
        total > 0 && hasDetailedRaceData ? (demo.byRace.twoOrMoreRaces / total) * 100 : null,
    };
  });

  if (enrollmentData.length === 0) {
    return null;
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        Student Demographics
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Enrollment Trend */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">
            Enrollment Over Time
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={enrollmentData}>
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
                <Line
                  type="monotone"
                  dataKey="undergraduate"
                  name="Undergraduate"
                  stroke={schoolColor}
                  strokeWidth={3}
                  dot={{ fill: schoolColor, r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="graduate"
                  name="Graduate"
                  stroke="#27ae60"
                  strokeWidth={2}
                  dot={{ fill: "#27ae60", r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Demographics Trend Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">
            Demographics Over Time (% of Undergraduates)
          </h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={demographicsData} margin={{ bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis
                  dataKey="year"
                  tick={{ fontSize: 12, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: "#666" }}
                  axisLine={{ stroke: "#e5e5e5" }}
                  tickFormatter={(v) => `${v.toFixed(0)}%`}
                  domain={[0, 'auto']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "white",
                    border: "1px solid #e5e5e5",
                    borderRadius: "8px",
                  }}
                  formatter={(value) => [`${(value as number).toFixed(1)}%`, ""]}
                  labelFormatter={(label) => `${label}-${parseInt(label as string) + 1}`}
                />
                <Legend
                  verticalAlign="bottom"
                  wrapperStyle={{ paddingTop: 12 }}
                />
                <Line
                  type="monotone"
                  dataKey="white"
                  name={RACE_LABELS.white}
                  stroke={RACE_COLORS.white}
                  strokeWidth={2}
                  dot={{ fill: RACE_COLORS.white, r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="asian"
                  name={RACE_LABELS.asian}
                  stroke={RACE_COLORS.asian}
                  strokeWidth={2}
                  dot={{ fill: RACE_COLORS.asian, r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="hispanicLatino"
                  name={RACE_LABELS.hispanicLatino}
                  stroke={RACE_COLORS.hispanicLatino}
                  strokeWidth={2}
                  dot={{ fill: RACE_COLORS.hispanicLatino, r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="blackAfricanAmerican"
                  name={RACE_LABELS.blackAfricanAmerican}
                  stroke={RACE_COLORS.blackAfricanAmerican}
                  strokeWidth={2}
                  dot={{ fill: RACE_COLORS.blackAfricanAmerican, r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="international"
                  name={RACE_LABELS.international}
                  stroke={RACE_COLORS.international}
                  strokeWidth={2}
                  dot={{ fill: RACE_COLORS.international, r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="twoOrMoreRaces"
                  name={RACE_LABELS.twoOrMoreRaces}
                  stroke={RACE_COLORS.twoOrMoreRaces}
                  strokeWidth={2}
                  dot={{ fill: RACE_COLORS.twoOrMoreRaces, r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
          <div>
            <div className="text-gray-500">Undergraduates</div>
            <div className="font-semibold text-lg" style={{ color: schoolColor }}>
              {formatNumber(latestDemo.enrollment.undergraduate)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">Total Enrollment</div>
            <div className="font-semibold text-lg">
              {formatNumber(latestDemo.enrollment.total)}
            </div>
          </div>
          <div>
            <div className="text-gray-500">International</div>
            <div className="font-semibold text-lg text-purple-600">
              {((latestDemo.byRace.international / totalUndergrad) * 100).toFixed(0)}%
            </div>
          </div>
          <div>
            <div className="text-gray-500">Students of Color</div>
            <div className="font-semibold text-lg text-green-600">
              {(100 - (latestDemo.byRace.white / totalUndergrad) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
