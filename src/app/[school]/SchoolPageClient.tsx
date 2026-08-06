"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { AdmissionsFactorImportance, SchoolData } from "@/lib/types";
import { formatNumber, formatPercent } from "@/utils/dataHelpers";
import {
  AdmissionsTrendChart,
  TestScoresTrendChart,
  CostsTrendChart,
  FinancialAidTrendChart,
  DemographicsTrendChart,
} from "@/components/charts";
import SaveSchoolButton from "@/components/SaveSchoolButton";
import SchoolNotes from "@/components/SchoolNotes";
import { useNotes } from "@/components/NotesContext";
import { useSavedSchools } from "@/components/SavedSchoolsContext";

interface SchoolPageClientProps {
  schoolData: SchoolData;
  schoolColor: string;
}

type AdmissionsFactorRow = [label: string, importance: AdmissionsFactorImportance];

const IMPORTANCE_LABELS: Record<AdmissionsFactorImportance, string> = {
  very_important: "Very Important",
  important: "Important",
  considered: "Considered",
  not_considered: "Not Considered",
};

const IMPORTANCE_ORDER: AdmissionsFactorImportance[] = [
  "very_important",
  "important",
  "considered",
  "not_considered",
];

export default function SchoolPageClient({
  schoolData,
  schoolColor,
}: SchoolPageClientProps) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const { data: session } = useSession();
  const { hasNote } = useNotes();
  const { promptSignIn } = useSavedSchools();
  const noteExists = hasNote(schoolData.slug);
  const [composing, setComposing] = useState(false);
  const showNotes = noteExists || composing;
  const notesRef = useRef<HTMLDivElement>(null);

  function handleAddNote() {
    if (!session) {
      promptSignIn({
        icon: "📝",
        title: "Sign in to add notes",
        description:
          "Keep private notes on any school — reminders, pros and cons, people to contact. Sign in with Google to get started.",
      });
      return;
    }
    setComposing(true);
  }

  useEffect(() => {
    if (composing) {
      notesRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [composing]);

  const years = Object.keys(schoolData.years).sort();
  const latestYear = years[years.length - 1];
  const latestData = schoolData.years[latestYear];
  const yearRange = `${years[0].split("-")[0]}-${years[years.length - 1].split("-")[1]}`;
  const admissionsFactors = schoolData.profile?.admissionsFactors;
  const academicFactors: AdmissionsFactorRow[] = admissionsFactors
    ? [
        ["Rigor of secondary school record", admissionsFactors.academic.rigorOfSecondarySchoolRecord],
        ["Class rank", admissionsFactors.academic.classRank],
        ["Academic GPA", admissionsFactors.academic.academicGpa],
        ["Standardized test scores", admissionsFactors.academic.standardizedTestScores],
        ["Application essay", admissionsFactors.academic.applicationEssay],
        ["Recommendation(s)", admissionsFactors.academic.recommendations],
      ]
    : [];
  const nonacademicFactors: AdmissionsFactorRow[] = admissionsFactors
    ? [
        ["Interview", admissionsFactors.nonacademic.interview],
        ["Extracurricular activities", admissionsFactors.nonacademic.extracurricularActivities],
        ["Talent/ability", admissionsFactors.nonacademic.talentAbility],
        ["Character/personal qualities", admissionsFactors.nonacademic.characterPersonalQualities],
        ["First generation", admissionsFactors.nonacademic.firstGeneration],
        ["Alumni/ae relation", admissionsFactors.nonacademic.alumniRelation],
        ["Geographical residence", admissionsFactors.nonacademic.geographicalResidence],
        ["State residency", admissionsFactors.nonacademic.stateResidency],
        ["Religious affiliation/commitment", admissionsFactors.nonacademic.religiousAffiliationCommitment],
        ["Volunteer work", admissionsFactors.nonacademic.volunteerWork],
        ["Work experience", admissionsFactors.nonacademic.workExperience],
        ["Level of applicant's interest", admissionsFactors.nonacademic.levelOfApplicantsInterest],
      ]
    : [];

  const renderImportanceCell = (
    activeImportance: AdmissionsFactorImportance,
    columnImportance: AdmissionsFactorImportance
  ) => {
    if (activeImportance !== columnImportance) return null;
    return <span aria-label={IMPORTANCE_LABELS[activeImportance]} style={{ color: schoolColor, opacity: 0.85, fontSize: "1.1rem", fontWeight: 600 }}>✓</span>;
  };

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Header Banner */}
      <div
        className="py-10 px-4 text-center text-white"
        style={{
          background: `linear-gradient(135deg, ${schoolColor} 0%, ${schoolColor}dd 100%)`,
        }}
      >
        <Link
          href="/schools"
          className="inline-flex items-center text-white/80 hover:text-white text-sm mb-4 transition-colors"
        >
          <svg
            className="w-4 h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Schools
        </Link>
        <h1 className="text-3xl md:text-4xl font-bold mb-2">
          {schoolData.name}
        </h1>
        <p className="text-white/80 text-sm md:text-base mb-4">
          Admissions Data Dashboard | Common Data Set {yearRange}
        </p>
        <div className="flex justify-center gap-2">
          <SaveSchoolButton
            schoolSlug={schoolData.slug}
            schoolName={schoolData.name}
            variant="button"
          />
          {!noteExists && (
            <button
              onClick={handleAddNote}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors bg-white/10 border border-white/30 text-white hover:bg-white/20"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              <span>Add note</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8 -mt-4">
        {/* Key Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="stat-card">
            <div className="label">Total Applications</div>
            <div className="value">{formatNumber(latestData.admissions.applied)}</div>
            <div className="subtext">{latestYear}</div>
          </div>
          <div className="stat-card">
            <div className="label">Acceptance Rate</div>
            <div className="value">{formatPercent(latestData.admissions.acceptanceRate)}</div>
            <div className="subtext">{latestYear}</div>
          </div>
          <div className="stat-card">
            <div className="label">Enrolled Students</div>
            <div className="value">{formatNumber(latestData.admissions.enrolled)}</div>
            <div className="subtext">{latestYear}</div>
          </div>
          <div className="stat-card">
            <div className="label">SAT Middle 50%</div>
            <div className="value">
              {typeof latestData.testScores.sat?.composite?.p25 === "number" &&
              typeof latestData.testScores.sat.composite.p75 === "number"
                ? `${latestData.testScores.sat.composite.p25}-${latestData.testScores.sat.composite.p75}`
                : "N/A"}
            </div>
            <div className="subtext">{latestYear}</div>
          </div>
        </div>

        {/* Notes — only rendered once a note exists or the user is composing one */}
        {showNotes && (
          <div className="mb-8" ref={notesRef}>
            <SchoolNotes
              schoolSlug={schoolData.slug}
              schoolColor={schoolColor}
              startEditing={composing && !noteExists}
              onClose={() => setComposing(false)}
            />
          </div>
        )}

        {/* Charts */}
        <div className="space-y-6">
          {mounted && (
            <>
              <AdmissionsTrendChart
                yearData={schoolData.years}
                schoolColor={schoolColor}
              />

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TestScoresTrendChart
                  yearData={schoolData.years}
                  schoolColor={schoolColor}
                />
                <FinancialAidTrendChart
                  yearData={schoolData.years}
                  schoolColor={schoolColor}
                />
              </div>

              <CostsTrendChart
                yearData={schoolData.years}
                schoolColor={schoolColor}
              />

              <DemographicsTrendChart
                yearData={schoolData.years}
                schoolColor={schoolColor}
              />
            </>
          )}

          {admissionsFactors && (
            <div className="card p-6" style={{ backgroundColor: "#ffffff" }}>
              <div className="flex flex-col gap-2 mb-4 md:flex-row md:items-end md:justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">
                    Admissions Factors
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Relative importance reported in the latest available Common Data Set.
                  </p>
                </div>
                <div className="text-sm text-gray-500">
                  Source: CDS {admissionsFactors.sourceYear}, Section {admissionsFactors.section}
                </div>
              </div>

              {/* Mobile: 2-column layout (factor + rating label) */}
              <div className="md:hidden">
                <table className="data-table compact w-full">
                  <thead>
                    <tr>
                      <th style={{ textAlign: "left" }}>Factor</th>
                      <th style={{ textAlign: "right" }}>Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { label: "Academic", rows: academicFactors },
                      { label: "Nonacademic", rows: nonacademicFactors },
                    ].map(({ label, rows }) => (
                      <React.Fragment key={`mobile-group-${label}`}>
                        <tr style={{ backgroundColor: `${schoolColor}18`, borderTop: `2px solid ${schoolColor}40` }}>
                          <td
                            colSpan={2}
                            style={{ fontWeight: 700, fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", color: schoolColor }}
                          >
                            {label}
                          </td>
                        </tr>
                        {rows.map(([rowLabel, importance]) => (
                          <tr key={`mobile-${label}-${rowLabel}`}>
                            <td style={{ textAlign: "left" }}>{rowLabel}</td>
                            <td style={{ textAlign: "right", color: schoolColor, fontWeight: 500, fontSize: "0.8rem", whiteSpace: "nowrap" }}>
                              {IMPORTANCE_LABELS[importance]}
                            </td>
                          </tr>
                        ))}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Desktop: full checkmark grid */}
              <div className="hidden md:block overflow-x-auto">
                <table className="data-table compact" style={{ tableLayout: "fixed" }}>
                  <colgroup>
                    <col style={{ width: "40%" }} />
                    <col style={{ width: "15%" }} />
                    <col style={{ width: "15%" }} />
                    <col style={{ width: "15%" }} />
                    <col style={{ width: "15%" }} />
                  </colgroup>
                  <thead>
                    <tr>
                      <th style={{ textAlign: "left" }}>Factor</th>
                      <th style={{ textAlign: "center" }}>Very Important</th>
                      <th style={{ textAlign: "center" }}>Important</th>
                      <th style={{ textAlign: "center" }}>Considered</th>
                      <th style={{ textAlign: "center" }}>Not Considered</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ backgroundColor: `${schoolColor}18`, borderTop: `2px solid ${schoolColor}40` }}>
                      <td
                        colSpan={5}
                        style={{ textAlign: "left", fontWeight: 700, fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", color: schoolColor }}
                      >
                        Academic
                      </td>
                    </tr>
                    {academicFactors.map(([label, importance]) => (
                      <tr key={`academic-${label}`}>
                        <td style={{ textAlign: "left" }}>{label}</td>
                        {IMPORTANCE_ORDER.map((columnImportance) => (
                          <td
                            key={`academic-${label}-${columnImportance}`}
                            style={{ textAlign: "center" }}
                          >
                            {renderImportanceCell(importance, columnImportance)}
                          </td>
                        ))}
                      </tr>
                    ))}
                    <tr style={{ backgroundColor: `${schoolColor}18`, borderTop: `2px solid ${schoolColor}40` }}>
                      <td
                        colSpan={5}
                        style={{ textAlign: "left", fontWeight: 700, fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", color: schoolColor }}
                      >
                        Nonacademic
                      </td>
                    </tr>
                    {nonacademicFactors.map(([label, importance]) => (
                      <tr key={`nonacademic-${label}`}>
                        <td style={{ textAlign: "left" }}>{label}</td>
                        {IMPORTANCE_ORDER.map((columnImportance) => (
                          <td
                            key={`nonacademic-${label}-${columnImportance}`}
                            style={{ textAlign: "center" }}
                          >
                            {renderImportanceCell(importance, columnImportance)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
