import { z } from "zod";

const count = z.number().int().nonnegative();
const rate = z.number().min(0).max(1);
const dollars = z.number().nonnegative();
const percentiles = z.strictObject({
  p25: z.number().optional(),
  p50: z.number().optional(),
  p75: z.number().optional(),
});
const appliedAdmitted = z.strictObject({ applied: count.optional(), admitted: count.optional() });
const genderCounts = z.strictObject({
  applied: count.optional(),
  admitted: count.optional(),
  enrolled: count.optional(),
});

export const admissionsFactorImportance = z.enum([
  "very_important",
  "important",
  "considered",
  "not_considered",
]);

const admissionsFactors = z.strictObject({
  sourceYear: z.string(),
  sourcePdf: z.string(),
  section: z.string(),
  academic: z.strictObject({
    rigorOfSecondarySchoolRecord: admissionsFactorImportance,
    classRank: admissionsFactorImportance,
    academicGpa: admissionsFactorImportance,
    standardizedTestScores: admissionsFactorImportance,
    applicationEssay: admissionsFactorImportance,
    recommendations: admissionsFactorImportance,
  }),
  nonacademic: z.strictObject({
    interview: admissionsFactorImportance,
    extracurricularActivities: admissionsFactorImportance,
    talentAbility: admissionsFactorImportance,
    characterPersonalQualities: admissionsFactorImportance,
    firstGeneration: admissionsFactorImportance,
    alumniRelation: admissionsFactorImportance,
    geographicalResidence: admissionsFactorImportance,
    stateResidency: admissionsFactorImportance,
    religiousAffiliationCommitment: admissionsFactorImportance,
    volunteerWork: admissionsFactorImportance,
    workExperience: admissionsFactorImportance,
    levelOfApplicantsInterest: admissionsFactorImportance,
  }),
  notes: z.string().optional(),
});

const admissions = z.strictObject({
  applied: count.optional(),
  admitted: count.optional(),
  enrolled: count.optional(),
  acceptanceRate: rate.optional(),
  yield: rate.optional(),
  earlyDecision: appliedAdmitted.optional(),
  earlyAction: appliedAdmitted.optional(),
  byGender: z.strictObject({ men: genderCounts, women: genderCounts }).optional(),
});

const testScores = z.strictObject({
  sat: z
    .strictObject({
      composite: percentiles.optional(),
      readingWriting: percentiles.optional(),
      math: percentiles.optional(),
      submissionRate: rate.optional(),
    })
    .optional(),
  act: z
    .strictObject({
      composite: percentiles.optional(),
      submissionRate: rate.optional(),
    })
    .optional(),
});

const demographics = z.strictObject({
  enrollment: z.strictObject({
    total: count.optional(),
    undergraduate: count.optional(),
    graduate: count.optional(),
  }),
  byRace: z.strictObject({
    international: count.optional(),
    hispanicLatino: count.optional(),
    blackAfricanAmerican: count.optional(),
    white: count.optional(),
    asian: count.optional(),
    americanIndianAlaskaNative: count.optional(),
    nativeHawaiianPacificIslander: count.optional(),
    twoOrMoreRaces: count.optional(),
    unknown: count.optional(),
  }),
  byResidency: z
    .strictObject({ inState: count, outOfState: count, international: count })
    .optional(),
});

const costs = z.strictObject({
  tuition: dollars.optional(),
  fees: dollars.optional(),
  roomAndBoard: dollars.optional(),
  totalCOA: dollars.optional(),
});

const financialAid = z.strictObject({
  percentReceivingAid: rate.optional(),
  averageAidPackage: dollars.optional(),
  averageNeedBasedGrant: dollars.optional(),
  percentNeedFullyMet: rate.optional(),
  averageNetPrice: dollars.optional(),
});

export const yearDataSchema = z.strictObject({
  admissions,
  testScores,
  demographics,
  costs,
  financialAid,
});

export const schoolDataSchema = z.strictObject({
  name: z.string().min(1),
  slug: z.string().regex(/^[a-z0-9]+$/),
  profile: z.strictObject({ admissionsFactors: admissionsFactors.optional() }).optional(),
  years: z.record(z.string().regex(/^\d{4}-\d{4}$/), yearDataSchema),
});
