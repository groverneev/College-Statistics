export type UCDiscipline =
  | "Architecture"
  | "Arts & Humanities"
  | "Business"
  | "Computer Science"
  | "Education"
  | "Engineering"
  | "Life Sciences"
  | "Nursing"
  | "Other Health Science"
  | "Other/Interdisciplinary"
  | "Pharmacy"
  | "Physical Sciences/Math"
  | "Public Admin"
  | "Public Health"
  | "Social Sciences"
  | "Undeclared";

export interface UCDisciplineData {
  applicants: number;
  admits: number | null;
  enrollees: number | null;
  admitGpaRange: [number, number] | null; // [25th, 75th] pctl
  enrolleeGpaRange: [number, number] | null;
}

export interface UCCampusYear {
  campusCode: string;
  name: string;
  overall: UCDisciplineData;
  disciplines: Partial<Record<UCDiscipline, UCDisciplineData>>;
}

export interface UCYearData {
  year: number;
  fallTerm: string;
  campuses: Record<string, UCCampusYear>;
}

export const UC_CAMPUS_ORDER = [
  "UCB", "UCD", "UCI", "UCLA", "UCM", "UCR", "UCSD", "UCSB", "UCSC",
];

export const UC_CAMPUS_NAMES: Record<string, string> = {
  UCB: "UC Berkeley",
  UCD: "UC Davis",
  UCI: "UC Irvine",
  UCLA: "UCLA",
  UCM: "UC Merced",
  UCR: "UC Riverside",
  UCSD: "UC San Diego",
  UCSB: "UC Santa Barbara",
  UCSC: "UC Santa Cruz",
};

export const UC_CAMPUS_COLORS: Record<string, string> = {
  UCB: "#003262",
  UCD: "#022851",
  UCI: "#0064A4",
  UCLA: "#2D68C4",
  UCM: "#002856",
  UCR: "#003DA5",
  UCSD: "#182B49",
  UCSB: "#003660",
  UCSC: "#003C6C",
};
