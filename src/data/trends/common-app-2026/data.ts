// Data for "2026 Application Season: Five Fault Lines"
// Source: Common App "Deadline Update, 2025-2026: First-year application trends through February 1"
// Published: February 12, 2026. Covers 913 returning member institutions.

// ─── Section 1: Overall platform stats ───────────────────────────────────────

export interface PlatformStat {
  label: string;
  value2025: string;
  value2026: string;
  changePct: number;
  note: string;
}

export const platformStats: PlatformStat[] = [
  {
    label: "First-Year Applicants",
    value2025: "1,368,306",
    value2026: "1,401,214",
    changePct: 2,
    note: "Distinct students submitting at least one application",
  },
  {
    label: "Total Applications",
    value2025: "8,715,557",
    value2026: "9,188,630",
    changePct: 5,
    note: "Across 913 returning member institutions",
  },
  {
    label: "Apps per Applicant",
    value2025: "6.37",
    value2026: "6.56",
    changePct: 3,
    note: "Students are applying to more schools on average",
  },
];

// ─── Section 2: Demographic growth rates ─────────────────────────────────────

export interface GroupGrowthRow {
  group: string;
  growth: number; // % change vs same point in 2024-25 season
}

// Sorted roughly from fastest to slowest growth (mix of demographic groups)
export const demographicGrowth: GroupGrowthRow[] = [
  { group: "Black / African American", growth: 9 },
  { group: "Below-Median Income ZIP", growth: 8 },
  { group: "Two or More Races", growth: 7 },
  { group: "First-Generation", growth: 7 },
  { group: "Fee Waiver Eligible", growth: 6 },
  { group: "URM Overall", growth: 5 },
  { group: "Female", growth: 4 },
  { group: "Non-URM", growth: 3 },
  { group: "All Applicants", growth: 2 },
  { group: "Above-Median Income ZIP", growth: 2 },
  { group: "Male", growth: 1 },
  { group: "Fee Waiver Ineligible", growth: 0 },
  { group: "Continuing-Generation", growth: 0 },
];

// ─── Section 3: International applicants ─────────────────────────────────────

export interface RegionRow {
  region: string;
  growth: number;
}

export const internationalByRegion: RegionRow[] = [
  { region: "Americas", growth: 3 },
  { region: "All International", growth: -9 },
  { region: "Asia", growth: -9 },
  { region: "Africa", growth: -16 },
];

export interface CountryRow {
  country: string;
  growth: number;
}

// Countries with notable declines (all explicitly stated in report)
export const countryDeclines: CountryRow[] = [
  { country: "Ghana", growth: -34 },
  { country: "Ethiopia", growth: -29 },
  { country: "Nigeria", growth: -16 },
  { country: "India", growth: -14 },
];

// Countries with notable gains (explicitly stated in report)
export const countryGains: CountryRow[] = [
  { country: "Venezuela", growth: 136 },
  { country: "Honduras", growth: 54 },
];

// ─── Section 4: Test score reporting ─────────────────────────────────────────

export interface ScoreReportingRow {
  group: string;
  growth: number;
}

export const scoreReportingGrowth: ScoreReportingRow[] = [
  { group: "Score Reporters", growth: 11 },
  { group: "Non-Reporters", growth: -5 },
];

// % of Common App members *requiring* test scores over time
// 2019-20 and 2023-24 through 2025-26 are explicitly cited in the report
export interface TestRequirementRow {
  season: string;
  pctRequiring: number;
}

export const testRequirementHistory: TestRequirementRow[] = [
  { season: "2019-20", pctRequiring: 55 },
  { season: "2023-24", pctRequiring: 4 },
  { season: "2024-25", pctRequiring: 5 },
  { season: "2025-26", pctRequiring: 5 },
];

// Groups less likely to submit a test score (qualitative, from report text)
export const lowerScoreSubmissionGroups = [
  "First-generation applicants",
  "URM applicants",
  "Fee-waiver-eligible applicants",
  "Students from below-median income ZIP codes",
];

// ─── Section 5: Application growth by selectivity ────────────────────────────

export interface SelectivityRow {
  band: string;
  admitRange: string;
  growth: number;
}

// From report: Most Selective (<25% admit rate) grew +3%;
// all other bands grew 6-7%. Public +6%, Private +5%.
export const selectivityGrowth: SelectivityRow[] = [
  { band: "Most Selective", admitRange: "< 25%", growth: 3 },
  { band: "Highly Selective", admitRange: "25 – 49%", growth: 7 },
  { band: "More Selective", admitRange: "50 – 74%", growth: 6 },
  { band: "Less Selective", admitRange: "≥ 75%", growth: 6 },
];

// ─── Narrative text ───────────────────────────────────────────────────────────

export const lede = `
Through February 1, 2026, more students have applied to college via Common App than ever before —
1.4 million applicants sending 9.2 million applications across 913 institutions. The headline number
suggests a boom. But beneath it, the 2025-2026 cycle reveals five sharp fault lines: who is surging,
who is retreating, where test scores stand, and why the nation's most selective schools are growing
the slowest of all.
`.trim();

export const takeaways = [
  "9,188,630 total applications submitted through Feb 1 — up 5% from 2024-25; apps per applicant rose from 6.37 to 6.56",
  "Black/African American applicants grew the fastest (+9%); first-generation and Two or More Races each grew +7%",
  "Below-median income ZIP codes drove growth at +8% — four times the rate of above-median income ZIPs (+2%)",
  "International applicants fell 9% overall; India down 14%, Ghana down 34%, Africa as a whole down 16%",
  "Venezuela (+136%) and Honduras (+54%) were the top-gaining countries; Americas region up +3%",
  "Score reporters grew +11% while non-reporters declined 5% — reporters now outnumber non-reporters early in the season",
  "Most selective schools (admit rate < 25%) saw only +3% application growth; all other selectivity bands grew 6–7%",
  "63.5% of member institutions saw stable or growing application volume; 36.5% saw a decline",
];
