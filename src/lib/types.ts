export interface SchoolData {
  name: string;
  slug: string;
  profile?: SchoolProfile;
  years: {
    [year: string]: YearData;
  };
}

export interface SchoolProfile {
  admissionsFactors?: AdmissionsFactorsData;
}

export type AdmissionsFactorImportance =
  | "very_important"
  | "important"
  | "considered"
  | "not_considered";

export interface AdmissionsFactorsData {
  sourceYear: string;
  sourcePdf: string;
  section: string;
  academic: {
    rigorOfSecondarySchoolRecord: AdmissionsFactorImportance;
    classRank: AdmissionsFactorImportance;
    academicGpa: AdmissionsFactorImportance;
    standardizedTestScores: AdmissionsFactorImportance;
    applicationEssay: AdmissionsFactorImportance;
    recommendations: AdmissionsFactorImportance;
  };
  nonacademic: {
    interview: AdmissionsFactorImportance;
    extracurricularActivities: AdmissionsFactorImportance;
    talentAbility: AdmissionsFactorImportance;
    characterPersonalQualities: AdmissionsFactorImportance;
    firstGeneration: AdmissionsFactorImportance;
    alumniRelation: AdmissionsFactorImportance;
    geographicalResidence: AdmissionsFactorImportance;
    stateResidency: AdmissionsFactorImportance;
    religiousAffiliationCommitment: AdmissionsFactorImportance;
    volunteerWork: AdmissionsFactorImportance;
    workExperience: AdmissionsFactorImportance;
    levelOfApplicantsInterest: AdmissionsFactorImportance;
  };
  notes?: string;
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
    composite: { p25: number; p50?: number; p75: number };
    readingWriting: { p25: number; p50?: number; p75: number };
    math: { p25: number; p50?: number; p75: number };
    submissionRate: number;
  };
  act?: {
    composite: { p25: number; p50?: number; p75: number };
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
  byResidency?: {
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
  percentReceivingAid?: number;
  averageAidPackage?: number;
  averageNeedBasedGrant?: number;
  percentNeedFullyMet?: number;
  averageNetPrice?: number;
}
