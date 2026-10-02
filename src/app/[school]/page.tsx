import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getSchoolColor, schoolDataMap } from "@/data/schools";
import { pageMetadata } from "@/lib/seo";
import { getLatestYear } from "@/utils/dataHelpers";
import { buildSchoolDescription, buildSchoolSummary } from "@/utils/schoolSummary";
import SchoolPageClient from "./SchoolPageClient";

// Generate static params for all schools
export function generateStaticParams() {
  return Object.keys(schoolDataMap).map((school) => ({
    school: school,
  }));
}

interface PageProps {
  params: Promise<{ school: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { school } = await params;
  const schoolData = schoolDataMap[school.toLowerCase()];
  if (!schoolData) return {};

  return pageMetadata({
    title: `${schoolData.name} Acceptance Rate & Admissions Statistics (${getLatestYear(schoolData)})`,
    description: buildSchoolDescription(schoolData),
    path: `/${schoolData.slug}`,
    defaultImage: false,
  });
}

export default async function SchoolPage({ params }: PageProps) {
  const { school } = await params;
  const schoolSlug = school.toLowerCase();
  const schoolData = schoolDataMap[schoolSlug];

  if (!schoolData) {
    notFound();
  }

  const schoolColor = getSchoolColor(schoolData.slug);

  return (
    <SchoolPageClient
      schoolData={schoolData}
      schoolColor={schoolColor}
      summary={buildSchoolSummary(schoolData)}
    />
  );
}
