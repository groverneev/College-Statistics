import { SchoolData } from "@/lib/types";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  getSortedYears,
} from "@/utils/dataHelpers";

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function satRange(school: SchoolData, year: string): string | null {
  const composite = school.years[year]?.testScores.sat?.composite;
  return isNumber(composite?.p25) && isNumber(composite?.p75)
    ? `${composite.p25}–${composite.p75}`
    : null;
}

// Short, number-led description for <meta name="description"> and social cards.
export function buildSchoolDescription(school: SchoolData): string {
  const years = getSortedYears(school);
  const latestYear = years[years.length - 1];
  const admissions = school.years[latestYear]?.admissions;
  const sat = satRange(school, latestYear);

  const facts: string[] = [];
  if (isNumber(admissions?.acceptanceRate)) {
    facts.push(
      `${school.name}'s acceptance rate was ${formatPercent(admissions.acceptanceRate)} in ${latestYear}` +
        (isNumber(admissions.applied)
          ? ` with ${formatNumber(admissions.applied)} applicants.`
          : ".")
    );
  }
  if (sat) {
    facts.push(`Middle 50% SAT: ${sat}.`);
  }

  const lead = facts.length > 0 ? `${facts.join(" ")} ` : "";
  return `${lead}See admissions trends, test scores, tuition, financial aid and demographics from the Common Data Set.`;
}

// Plain-language overview rendered on the school page so the key numbers are
// readable as text (by people and crawlers), not only inside charts.
export function buildSchoolSummary(school: SchoolData): string[] {
  const years = getSortedYears(school);
  const firstYear = years[0];
  const latestYear = years[years.length - 1];
  const latest = school.years[latestYear];
  const first = school.years[firstYear];
  const sentences: string[] = [];

  const { applied, acceptanceRate, enrolled, yield: yieldRate } = latest.admissions;
  if (isNumber(applied) && isNumber(acceptanceRate)) {
    let sentence = `${school.name} received ${formatNumber(applied)} applications for ${latestYear} and admitted ${formatPercent(acceptanceRate)} of applicants`;
    if (isNumber(enrolled)) {
      sentence += `; ${formatNumber(enrolled)} admitted students enrolled`;
      if (isNumber(yieldRate)) {
        sentence += ` (a ${formatPercent(yieldRate)} yield)`;
      }
    }
    sentences.push(`${sentence}.`);
  } else if (isNumber(acceptanceRate)) {
    sentences.push(
      `${school.name}'s acceptance rate was ${formatPercent(acceptanceRate)} in ${latestYear}.`
    );
  }

  const firstRate = first?.admissions.acceptanceRate;
  if (firstYear !== latestYear && isNumber(firstRate) && isNumber(acceptanceRate)) {
    sentences.push(
      `That compares with an acceptance rate of ${formatPercent(firstRate)} in ${firstYear}.`
    );
  }

  const sat = satRange(school, latestYear);
  const act = latest.testScores.act?.composite;
  const hasAct = isNumber(act?.p25) && isNumber(act?.p75);
  if (sat && hasAct) {
    sentences.push(
      `The middle 50% of enrolled first-year students scored ${sat} on the SAT and ${act!.p25}–${act!.p75} on the ACT.`
    );
  } else if (sat) {
    sentences.push(`The middle 50% of enrolled first-year students scored ${sat} on the SAT.`);
  } else if (hasAct) {
    sentences.push(
      `The middle 50% of enrolled first-year students scored ${act!.p25}–${act!.p75} on the ACT.`
    );
  }

  const totalCOA = latest.costs.totalCOA;
  const avgGrant = latest.financialAid.averageNeedBasedGrant;
  if (isNumber(totalCOA)) {
    let sentence = `The total cost of attendance was ${formatCurrency(totalCOA)}`;
    if (isNumber(avgGrant)) {
      sentence += `, and the average need-based grant was ${formatCurrency(avgGrant)}`;
    }
    sentences.push(`${sentence}.`);
  }

  return sentences;
}
