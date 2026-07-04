import Link from "next/link";
import { allSchools, getSchoolColor } from "@/data/schools";
import { getSortedYears } from "@/utils/dataHelpers";

interface LeaderboardRow {
  slug: string;
  name: string;
  color: string;
  firstYear: string;
  lastYear: string;
  firstRate: number;
  lastRate: number;
  dropPoints: number;
}

function buildLeaderboard(): LeaderboardRow[] {
  const rows: LeaderboardRow[] = [];

  for (const school of allSchools) {
    const years = getSortedYears(school);
    if (years.length < 2) continue;

    const firstYear = years[0];
    const lastYear = years[years.length - 1];
    const firstRate = school.years[firstYear]?.admissions.acceptanceRate;
    const lastRate = school.years[lastYear]?.admissions.acceptanceRate;
    if (!firstRate || !lastRate) continue;

    const dropPoints = (firstRate - lastRate) * 100;
    if (dropPoints <= 0) continue;

    rows.push({
      slug: school.slug,
      name: school.name,
      color: getSchoolColor(school.slug),
      firstYear,
      lastYear,
      firstRate,
      lastRate,
      dropPoints,
    });
  }

  return rows.sort((a, b) => b.dropPoints - a.dropPoints).slice(0, 5);
}

function pct(rate: number): string {
  return `${(rate * 100).toFixed(1)}%`;
}

function startYear(academicYear: string): string {
  return academicYear.split("-")[0];
}

export default function HomeDataTeaser() {
  const rows = buildLeaderboard();
  if (rows.length === 0) return null;

  const span = `${startYear(rows[0].firstYear)}–${startYear(rows[0].lastYear)}`;

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex items-end justify-between mb-2">
        <h2 className="text-2xl font-semibold text-gray-800">
          Where admissions got hardest
        </h2>
        <Link
          href="/schools"
          className="text-sm font-medium text-blue-600 hover:text-blue-700 whitespace-nowrap"
        >
          See all schools &rarr;
        </Link>
      </div>
      <p className="text-sm text-gray-500 mb-6">
        Largest drop in acceptance rate from each school&apos;s earliest to latest
        Common Data Set year.
      </p>

      <div className="card overflow-hidden">
        <ul className="divide-y divide-gray-100">
          {rows.map((row, index) => (
            <li key={row.slug}>
              <Link
                href={`/${row.slug}`}
                className="flex items-center gap-4 px-4 sm:px-6 py-4 hover:bg-gray-50 transition-colors"
              >
                <span className="w-6 text-lg font-bold text-gray-300 tabular-nums">
                  {index + 1}
                </span>
                <span
                  className="w-1.5 h-8 rounded-full flex-shrink-0"
                  style={{ backgroundColor: row.color }}
                  aria-hidden
                />
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-gray-800 truncate">
                    {row.name}
                  </div>
                  <div className="text-xs text-gray-500 tabular-nums">
                    {pct(row.firstRate)} &rarr; {pct(row.lastRate)}
                    <span className="hidden sm:inline">
                      {" "}
                      ({startYear(row.firstYear)}–{startYear(row.lastYear)})
                    </span>
                  </div>
                </div>
                <span className="text-sm font-bold text-red-600 tabular-nums whitespace-nowrap">
                  &minus;{row.dropPoints.toFixed(1)} pts
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
      <p className="text-xs text-gray-400 mt-3">
        Ranges vary by school; most cover {span}.
      </p>
    </div>
  );
}
