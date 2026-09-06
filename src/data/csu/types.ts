// Shapes for the CSU Explorer dataset produced by scripts/build_csu_data.py.
//
// A `null` anywhere in this data is a value the CSU suppressed at source. It is
// never a zero and never an estimate. See College-Data/csu/raw/SOURCE.md.

/** Entry level. `F` = first-time freshmen, `U` = undergraduate transfers. */
export type CSULevel = "F" | "U";

/** Applications, admissions and enrollment for one term. */
export interface CSUAdmissions {
  applied: number | null;
  admitted: number | null;
  enrolled: number | null;
}

/** Fall term counts keyed by year, e.g. `{ "2025": { ... } }`. */
export type CSUAdmissionsByYear = Record<string, CSUAdmissions>;

/** One campus and discipline area at one entry level, Fall 2025. */
export interface CSUCampusArea {
  campus: string;
  area: string;
  level: CSULevel;
  applied: number;
  admitted: number;
  enrolled: number | null;
}

/** Systemwide totals for one discipline area, Fall 2025, both entry levels. */
export interface CSUAreaTotals {
  applied: number;
  admitted: number;
  enrolled: number | null;
}

/** One major at one campus, Fall 2025 first-time freshmen. */
export interface CSUProgram {
  campus: string;
  area: string;
  major: string;
  applied: number;
  admitted: number;
  enrolled: number | null;
  /** Admitted as a percentage of applicants, one decimal place. */
  admitRate: number;
}

/** California a-g completion for one academic year, e.g. `"2024-25"`. */
export interface CSUStatewideYear {
  year: string;
  met: number | null;
  graduates: number | null;
  /** Percentage of graduates meeting CSU subject requirements. */
  rate: number | null;
}

/** California a-g completion for one county, most recent academic year. */
export interface CSUCounty {
  name: string;
  graduates: number;
  met: number | null;
  rate: number;
  /** The same rate in the earliest year on record, for change over time. */
  priorRate: number | null;
}

export interface CSUData {
  /** Fall terms covered by the admissions files, oldest first. */
  fallYears: number[];
  /** Academic years covered by the a-g files, oldest first. */
  academicYears: string[];
  system: CSUAdmissionsByYear;
  campuses: Record<string, CSUAdmissionsByYear>;
  /** Systemwide totals per entry level per Fall term. */
  byLevel: Record<CSULevel, Record<string, CSUAdmissions>>;
  campusAreas: CSUCampusArea[];
  areas: Record<string, CSUAreaTotals>;
  /** Lowest admit rates, Fall 2025 freshmen, programs above the size floor. */
  mostSelective: CSUProgram[];
  /** Highest application volume, same population. */
  largest: CSUProgram[];
  statewide: CSUStatewideYear[];
  counties: CSUCounty[];
}

/**
 * CalStateTEACH is a systemwide credential program rather than a campus. It
 * appears in the source campus export and is excluded from campus rankings.
 */
export const CSU_NON_CAMPUS = "CalStateTEACH";

/** Source campus keys mapped to the names each campus actually goes by. */
export const CSU_CAMPUS_NAMES: Record<string, string> = {
  Bakersfield: "CSU Bakersfield",
  CalStateTEACH: "CalStateTEACH",
  "Channel Islands": "CSU Channel Islands",
  Chico: "Chico State",
  "Dominguez Hills": "CSU Dominguez Hills",
  "East Bay": "Cal State East Bay",
  Fresno: "Fresno State",
  Fullerton: "Cal State Fullerton",
  Humboldt: "Cal Poly Humboldt",
  "Long Beach": "Cal State Long Beach",
  "Los Angeles": "Cal State LA",
  "Maritime Academy": "Cal Maritime",
  "Monterey Bay": "CSU Monterey Bay",
  Northridge: "CSU Northridge",
  Pomona: "Cal Poly Pomona",
  Sacramento: "Sacramento State",
  "San Bernardino": "CSU San Bernardino",
  "San Diego": "San Diego State",
  "San Francisco": "San Francisco State",
  "San Jose": "San José State",
  "San Luis Obispo": "Cal Poly SLO",
  "San Marcos": "CSU San Marcos",
  Sonoma: "Sonoma State",
  Stanislaus: "Stanislaus State",
};

/** Short labels for the CSU's broad discipline areas, for axes and headers. */
export const CSU_AREA_LABELS: Record<string, string> = {
  "Agriculture and Natural Resources": "Agriculture",
  "Architecture and Environmental Design": "Architecture",
  "Area Studies": "Area studies",
  "Biological Science": "Bio science",
  "Business and Management": "Business",
  Communications: "Communication",
  "Computer and Information Sciences": "Computing",
  Education: "Education",
  Engineering: "Engineering",
  "Fine and Applied Arts": "Arts",
  "Foreign Languages": "Languages",
  "Health Professions": "Health prof.",
  "Home Economics": "Home econ.",
  "Interdisciplinary Studies": "Interdisc.",
  Letters: "Letters",
  Mathematics: "Mathematics",
  "Physical Science": "Phys. science",
  Psychology: "Psychology",
  "Public Affairs and Services": "Public affairs",
  "Social Sciences": "Social science",
  Undeclared: "Undeclared",
  Unknown: "Unknown",
};

/** Entry level labels. */
export const CSU_LEVEL_LABELS: Record<CSULevel, string> = {
  F: "First-time freshmen",
  U: "Undergraduate transfers",
};
