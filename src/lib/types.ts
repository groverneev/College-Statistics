export interface SchoolData {
  name: string;
  slug: string;
  years: {
    [year: string]: YearData;
  };
}

export interface YearData {
  admissions: AdmissionsData;
  testScores: TestScoresData;
  demographics: DemographicsData;
  costs: CostsData;
  financialAid: FinancialAidData;
}

export interface AdmissionsData {
  applied: number;
  admitted: number;
  enrolled: number;
  acceptanceRate: number;
  yield: number;
  earlyDecision?: {
    applied: number;
    admitted: number;
  };
  earlyAction?: {
    applied: number;
    admitted: number;
  };
  byGender?: {
    men: { applied: number; admitted: number; enrolled: number };
    women: { applied: number; admitted: number; enrolled: number };
  };
}

export interface TestScoresData {
  sat?: {
    composite: { p25: number; p50: number; p75: number };
    readingWriting: { p25: number; p50: number; p75: number };
    math: { p25: number; p50: number; p75: number };
    submissionRate: number;
  };
  act?: {
    composite: { p25: number; p50: number; p75: number };
    submissionRate: number;
  };
}

export interface DemographicsData {
  enrollment: {
    total: number;
    undergraduate: number;
    graduate?: number;
  };
  byRace: {
    international: number;
    hispanicLatino: number;
    blackAfricanAmerican: number;
    white: number;
    asian: number;
    americanIndianAlaskaNative: number;
    nativeHawaiianPacificIslander: number;
    twoOrMoreRaces: number;
    unknown: number;
  };
  byResidency: {
    inState: number;
    outOfState: number;
    international: number;
  };
}

export interface CostsData {
  tuition: number;
  fees: number;
  roomAndBoard: number;
  totalCOA: number;
}

export interface FinancialAidData {
  percentReceivingAid: number;
  averageAidPackage: number;
  averageNeedBasedGrant: number;
  percentNeedFullyMet: number;
  averageNetPrice?: number;
}

export interface SchoolInfo {
  name: string;
  slug: string;
  color: string;
}

export const SCHOOL_COLORS: Record<string, string> = {
  brown: "#4E3629",
  bostonuniversity: "#CC0000",
  harvard: "#A51C30",
  yale: "#00356B",
  princeton: "#E77500",
  cornell: "#B31B1B",
  dartmouth: "#00693E",
  upenn: "#011F5B",
  stanford: "#8C1515",
  caltech: "#FF6C0C",
  ucla: "#2774AE",
  ucdavis: "#022851",
  uci: "#0064A4",
  columbia: "#1D4F91",
  georgiatech: "#B3A369",
  uiuc: "#13294B",
  mit: "#A31F34",
  northeastern: "#C8102E",
  notredame: "#0C2340",
  nyu: "#57068C",
  northwestern: "#4E2A84",
  purdue: "#CFB991",
  rice: "#00205B",
  duke: "#012169",
  emory: "#012169",
  umich: "#00274C",
  johnshopkins: "#002D72",
  vanderbilt: "#866D4B",
  ucberkeley: "#003262",
  uchicago: "#800000",
  cmu: "#C41230",
  usc: "#990000",
  utexasaustin: "#BF5700",
  uva: "#232D4B",
};
