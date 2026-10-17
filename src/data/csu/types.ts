export type CSULevel = "F" | "U";

export interface CSUAdmissions {
  applied: number | null;
  admitted: number | null;
  enrolled: number | null;
}

export type CSUAdmissionsByYear = Record<string, CSUAdmissions>;

export interface CSUCampusArea {
  campus: string;
  area: string;
  level: CSULevel;
  applied: number;
  admitted: number;
  enrolled: number | null;
}

export interface CSUAreaTotals {
  applied: number;
  admitted: number;
  enrolled: number | null;
}

export interface CSUProgram {
  campus: string;
  area: string;
  major: string;
  applied: number;
  admitted: number;
  enrolled: number | null;
  admitRate: number;
}

export interface CSUStatewideYear {
  year: string;
  met: number | null;
  graduates: number | null;
  rate: number | null;
}

export interface CSUCounty {
  name: string;
  graduates: number;
  met: number | null;
  rate: number;
  priorRate: number | null;
}

export interface CSUData {
  fallYears: number[];
  academicYears: string[];
  system: CSUAdmissionsByYear;
  campuses: Record<string, CSUAdmissionsByYear>;
  byLevel: Record<CSULevel, Record<string, CSUAdmissions>>;
  campusAreas: CSUCampusArea[];
  areas: Record<string, CSUAreaTotals>;
  mostSelective: CSUProgram[];
  largest: CSUProgram[];
  statewide: CSUStatewideYear[];
  counties: CSUCounty[];
}

export const CSU_NON_CAMPUS = "CalStateTEACH";

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

export const CSU_LEVEL_LABELS: Record<CSULevel, string> = {
  F: "First-time freshmen",
  U: "Undergraduate transfers",
};
