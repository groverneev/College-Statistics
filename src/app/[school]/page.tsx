import { notFound } from "next/navigation";
import { getSchoolColor, schoolDataMap } from "@/data/schools";
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
    />
  );
}
