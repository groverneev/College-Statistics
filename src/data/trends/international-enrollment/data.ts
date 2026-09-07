import { allSchools } from "@/data/schools";

const BASE_YEAR = "2016-2017";
const REPORT_YEAR = "2024-2025";

export interface InternationalShareRow {
  slug: string;
  school: string;
  shortName: string;
  year: string;
  international: number;
  undergraduate: number;
  share: number;
}

export interface InternationalComparisonRow {
  slug: string;
  school: string;
  shortName: string;
  baseShare: number;
  reportShare: number;
  change: number;
}

const shortNames: Record<string, string> = {
  bostonuniversity: "Boston U.",
  caltech: "Caltech",
  cmu: "Carnegie Mellon",
  columbia: "Columbia",
  dartmouth: "Dartmouth",
  emory: "Emory",
  georgetown: "Georgetown",
  harvard: "Harvard",
  johnshopkins: "Johns Hopkins",
  miami: "Miami",
  northeastern: "Northeastern",
  nyu: "NYU",
  rochester: "Rochester",
  uchicago: "Chicago",
  ucdavis: "UC Davis",
  uci: "UC Irvine",
  ucsandiego: "UC San Diego",
  uiuc: "UIUC",
  umd: "Maryland",
  umich: "Michigan",
  uncchapelhill: "UNC Chapel Hill",
  upenn: "Penn",
  usc: "USC",
  utexasaustin: "UT Austin",
  uva: "Virginia",
  uwashington: "Washington",
  vanderbilt: "Vanderbilt",
  wakeforest: "Wake Forest",
};

function getInternationalShare(
  school: (typeof allSchools)[number],
  year: string,
): Omit<InternationalShareRow, "slug" | "school" | "shortName" | "year"> | null {
  const yearData = school.years[year];
  const international = yearData?.demographics?.byRace?.international;
  const undergraduate = yearData?.demographics?.enrollment?.undergraduate;

  if (
    typeof international !== "number" ||
    typeof undergraduate !== "number" ||
    undergraduate <= 0
  ) {
    return null;
  }

  return {
    international,
    undergraduate,
    share: (international / undergraduate) * 100,
  };
}

function makeRow(
  school: (typeof allSchools)[number],
  year: string,
): InternationalShareRow | null {
  const values = getInternationalShare(school, year);
  if (!values) return null;

  return {
    slug: school.slug,
    school: school.name,
    shortName: shortNames[school.slug] ?? school.name,
    year,
    ...values,
  };
}

export const reportYear = REPORT_YEAR;
export const baseYear = BASE_YEAR;

export const reportRows = allSchools
  .map((school) => makeRow(school, REPORT_YEAR))
  .filter((row): row is InternationalShareRow => row !== null)
  .sort((a, b) => b.share - a.share);

export const chartRows = reportRows.slice(0, 15);

export const comparisonRows = allSchools
  .map((school) => {
    const base = makeRow(school, BASE_YEAR);
    const report = makeRow(school, REPORT_YEAR);
    if (!base || !report) return null;

    return {
      slug: school.slug,
      school: school.name,
      shortName: shortNames[school.slug] ?? school.name,
      baseShare: base.share,
      reportShare: report.share,
      change: report.share - base.share,
    };
  })
  .filter((row): row is InternationalComparisonRow => row !== null);

const comparisonSchoolSlugs = new Set(comparisonRows.map((row) => row.slug));
const annualYears = [
  "2016-2017",
  "2017-2018",
  "2018-2019",
  "2019-2020",
  "2020-2021",
  "2021-2022",
  "2022-2023",
  "2023-2024",
  "2024-2025",
];

function median(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle];
}

export const metrics = {
  reportSchoolCount: reportRows.length,
  comparisonSchoolCount: comparisonRows.length,
  schoolsAtLeastTenPercent: reportRows.filter((row) => row.share >= 10).length,
  medianBaseShare: median(comparisonRows.map((row) => row.baseShare)),
  medianReportShare: median(comparisonRows.map((row) => row.reportShare)),
  medianChange: median(comparisonRows.map((row) => row.change)),
  schoolsUp: comparisonRows.filter((row) => row.change > 0.5).length,
  schoolsDown: comparisonRows.filter((row) => row.change < -0.5).length,
  schoolsFlat: comparisonRows.filter((row) => Math.abs(row.change) <= 0.5).length,
};

export const annualMedianRows = annualYears.map((year) => {
  const rows = allSchools
    .filter((school) => comparisonSchoolSlugs.has(school.slug))
    .map((school) => makeRow(school, year))
    .filter((row): row is InternationalShareRow => row !== null);

  return {
    year: year.slice(0, 4),
    share: median(rows.map((row) => row.share)),
    schoolCount: rows.length,
  };
});

export const notableDeclines = [
  "ucsandiego",
  "purdue",
  "northeastern",
  "miami",
]
  .map((slug) => comparisonRows.find((row) => row.slug === slug))
  .filter((row): row is InternationalComparisonRow => row !== undefined);

// UC Davis has a sharp source-series break between 2018–19 and 2019–20. Keep it
// in the full data, but use a conservative set of named examples in the story chart.
const notableIncreases = ["dartmouth", "caltech", "vanderbilt", "uncchapelhill"]
  .map((slug) => comparisonRows.find((row) => row.slug === slug))
  .filter((row): row is InternationalComparisonRow => row !== undefined);

export const changeChartRows = [...notableDeclines, ...notableIncreases].sort(
  (a, b) => a.change - b.change,
);

export const lede = `
In 2024–25, ${metrics.schoolsAtLeastTenPercent} of the ${metrics.reportSchoolCount} schools in this
dataset reported international students making up at least 10% of their undergraduate
population. Across ${metrics.comparisonSchoolCount} schools with data at both endpoints,
the median share rose from ${metrics.medianBaseShare.toFixed(1)}% to
${metrics.medianReportShare.toFixed(1)}%, while individual school changes went in both directions.
`.trim();

export const factBullets = [
  `${metrics.schoolsAtLeastTenPercent} of ${metrics.reportSchoolCount} schools had international undergraduates equal to at least 10% of their undergraduate population in ${REPORT_YEAR}.`,
  `NYU reported ${reportRows[0]?.international.toLocaleString()} international undergraduates, equal to ${reportRows[0]?.share.toFixed(1)}% of its undergraduate population.`,
  `Carnegie Mellon, Rochester, and Boston University reported international shares of ${reportRows[1]?.share.toFixed(1)}%, ${reportRows[2]?.share.toFixed(1)}%, and ${reportRows[3]?.share.toFixed(1)}%, respectively.`,
  `Florida, Maryland, and UT Austin each reported international shares below 5% in ${REPORT_YEAR}.`,
  `Among ${metrics.comparisonSchoolCount} schools with data in both ${BASE_YEAR} and ${REPORT_YEAR}, the median international share was ${metrics.medianBaseShare.toFixed(1)}% in ${BASE_YEAR} and ${metrics.medianReportShare.toFixed(1)}% in ${REPORT_YEAR}.`,
  `${metrics.schoolsUp} schools gained more than half a percentage point, ${metrics.schoolsDown} declined by more than half a point, and ${metrics.schoolsFlat} were essentially flat.`,
  `UC San Diego, Purdue, Northeastern, and Miami each recorded declines of roughly six to seven percentage points over the period.`,
  `The comparison uses all undergraduate enrollment, not the international share of the entering class.`,
];

export interface SourceLink {
  label: string;
  url: string;
}

export const sourceLinks: SourceLink[] = [
  {
    label: "College Statistics school data and methodology",
    url: "/how-it-works",
  },
  {
    label: "Browse the school database",
    url: "/schools",
  },
];

export const sourceNote =
  "Source: CollegeStatistics.org analysis of institution-published Common Data Set records. The chart uses 2024–25, the latest year available for most schools; 2025–26 data is currently available for only eight schools. International students are the CDS-reported international/nonresident category divided by undergraduate enrollment.";
