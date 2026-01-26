import { SchoolData, SCHOOL_COLORS } from "@/lib/types";
import { getAvailableSchools } from "@/utils/dataHelpers";
import SchoolPageClient from "./SchoolPageClient";

// Import school data
import brownData from "@/data/schools/brown.json";
import caltechData from "@/data/schools/caltech.json";
import harvardData from "@/data/schools/harvard.json";
import princetonData from "@/data/schools/princeton.json";
import stanfordData from "@/data/schools/stanford.json";
import upennData from "@/data/schools/upenn.json";
import yaleData from "@/data/schools/yale.json";

const schoolDataMap: Record<string, SchoolData> = {
  brown: brownData as SchoolData,
  caltech: caltechData as SchoolData,
  harvard: harvardData as SchoolData,
  princeton: princetonData as SchoolData,
  stanford: stanfordData as SchoolData,
  upenn: upennData as SchoolData,
  yale: yaleData as SchoolData,
};

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
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          School Not Found
        </h1>
        <p className="text-gray-500">
          Data for &quot;{school}&quot; is not available yet.
        </p>
        <a href="/" className="text-blue-500 hover:underline mt-4 inline-block">
          Back to home
        </a>
      </div>
    );
  }

  const schoolColor = SCHOOL_COLORS[schoolData.slug] || "#4B5563";
  const availableSchools = getAvailableSchools();

  return (
    <SchoolPageClient
      schoolData={schoolData}
      schoolColor={schoolColor}
      availableSchools={availableSchools}
    />
  );
}
