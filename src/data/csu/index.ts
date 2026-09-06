import { csuData } from "./generated";
import {
  CSU_AREA_LABELS,
  CSU_CAMPUS_NAMES,
  CSU_NON_CAMPUS,
  type CSUAdmissions,
  type CSUCampusArea,
  type CSULevel,
} from "./types";

export * from "./types";
export { csuData };

/** The Fall term every single-year view reports on. */
export const CSU_LATEST_FALL = csuData.fallYears[csuData.fallYears.length - 1];
export const CSU_EARLIEST_FALL = csuData.fallYears[0];

/**
 * Discipline-level enrollment is suppressed in much of Fall 2021 and Fall 2022,
 * so discipline views report a single term rather than a trend that would show
 * a reporting gap as a collapse. Campus and systemwide totals are complete for
 * every year and are safe to chart across the full range.
 */
export const CSU_DISCIPLINE_FALL = CSU_LATEST_FALL;

export function admitRate(a: CSUAdmissions | { applied: number; admitted: number | null }): number | null {
  if (!a.applied || a.admitted == null) return null;
  return (100 * a.admitted) / a.applied;
}

export function yieldRate(a: CSUAdmissions): number | null {
  if (!a.admitted || a.enrolled == null) return null;
  return (100 * a.enrolled) / a.admitted;
}

export function campusName(key: string): string {
  return CSU_CAMPUS_NAMES[key] ?? key;
}

export function areaLabel(area: string): string {
  return CSU_AREA_LABELS[area] ?? area;
}

/** Campus keys, most selective first. Excludes the CalStateTEACH program. */
export const csuCampusesBySelectivity: string[] = Object.keys(csuData.campuses)
  .filter((key) => key !== CSU_NON_CAMPUS)
  .sort((a, b) => {
    const rateA = admitRate(csuData.campuses[a][String(CSU_LATEST_FALL)]) ?? Infinity;
    const rateB = admitRate(csuData.campuses[b][String(CSU_LATEST_FALL)]) ?? Infinity;
    return rateA - rateB;
  });

/** Campus keys in alphabetical order of the name each campus goes by. */
export const csuCampusesByName: string[] = [...csuCampusesBySelectivity].sort((a, b) =>
  campusName(a).localeCompare(campusName(b))
);

/** Discipline areas, largest application volume first. */
export const csuAreasByVolume: string[] = Object.keys(csuData.areas).sort(
  (a, b) => csuData.areas[b].applied - csuData.areas[a].applied
);

/** The areas wide enough to be worth a column in the campus/discipline matrix. */
export const csuMatrixAreas: string[] = csuAreasByVolume
  .filter((area) => area !== "Unknown")
  .slice(0, 12);

const areaIndex = new Map<string, CSUCampusArea>(
  csuData.campusAreas.map((row) => [`${row.campus}|${row.area}|${row.level}`, row])
);

export function campusArea(campus: string, area: string, level: CSULevel): CSUCampusArea | undefined {
  return areaIndex.get(`${campus}|${area}|${level}`);
}

/** Every discipline area a campus reports at one entry level, hardest first. */
export function campusAreasFor(campus: string, level: CSULevel): CSUCampusArea[] {
  return csuData.campusAreas
    .filter((row) => row.campus === campus && row.level === level && row.applied > 0)
    .sort((a, b) => (admitRate(a) ?? 100) - (admitRate(b) ?? 100));
}

/** A campus's totals at one entry level, summed across its discipline areas. */
export function campusLevelTotals(campus: string, level: CSULevel): CSUCampusArea {
  return csuData.campusAreas
    .filter((row) => row.campus === campus && row.level === level)
    .reduce<CSUCampusArea>(
      (total, row) => ({
        ...total,
        applied: total.applied + row.applied,
        admitted: total.admitted + row.admitted,
        enrolled: row.enrolled == null ? total.enrolled : (total.enrolled ?? 0) + row.enrolled,
      }),
      { campus, area: "All", level, applied: 0, admitted: 0, enrolled: null }
    );
}

export const csuStatewideLatest = csuData.statewide[csuData.statewide.length - 1];
export const csuStatewideEarliest = csuData.statewide[0];

/** Counties with the highest a-g completion first. */
export const csuCountiesByRate = [...csuData.counties].sort((a, b) => b.rate - a.rate);
