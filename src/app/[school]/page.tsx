import { SchoolData, SCHOOL_COLORS } from "@/lib/types";
import { getAvailableSchools } from "@/utils/dataHelpers";
import SchoolPageClient from "./SchoolPageClient";

// Import school data
import brownData from "@/data/schools/brown.json";
import bostonUniversityData from "@/data/schools/bostonuniversity.json";
import caltechData from "@/data/schools/caltech.json";
import cornellData from "@/data/schools/cornell.json";
import dartmouthData from "@/data/schools/dartmouth.json";
import harvardData from "@/data/schools/harvard.json";
import princetonData from "@/data/schools/princeton.json";
import stanfordData from "@/data/schools/stanford.json";
import uclaData from "@/data/schools/ucla.json";
import ucberkeleyData from "@/data/schools/ucberkeley.json";
import ucdavisData from "@/data/schools/ucdavis.json";
import ucsanDiegoData from "@/data/schools/ucsandiego.json";
import uciData from "@/data/schools/uci.json";
import uchicagoData from "@/data/schools/uchicago.json";
import uiucData from "@/data/schools/uiuc.json";
import uncChapelHillData from "@/data/schools/uncchapelhill.json";
import upennData from "@/data/schools/upenn.json";
import uscData from "@/data/schools/usc.json";
import uwmadisonData from "@/data/schools/uwmadison.json";
import uwashingtonData from "@/data/schools/uwashington.json";
import utexasaustinData from "@/data/schools/utexasaustin.json";
import uvaData from "@/data/schools/uva.json";
import yaleData from "@/data/schools/yale.json";
import columbiaData from "@/data/schools/columbia.json";
import cmuData from "@/data/schools/cmu.json";
import mitData from "@/data/schools/mit.json";
import northeasternData from "@/data/schools/northeastern.json";
import notreDameData from "@/data/schools/notredame.json";
import nyuData from "@/data/schools/nyu.json";
import northwesternData from "@/data/schools/northwestern.json";
import purdueData from "@/data/schools/purdue.json";
import riceData from "@/data/schools/rice.json";
import umichData from "@/data/schools/umich.json";
import dukeData from "@/data/schools/duke.json";
import emoryData from "@/data/schools/emory.json";
import georgiaTechData from "@/data/schools/georgiatech.json";
import johnsHopkinsData from "@/data/schools/johnshopkins.json";
import vanderbiltData from "@/data/schools/vanderbilt.json";

const schoolDataMap: Record<string, SchoolData> = {
  brown: brownData as SchoolData,
  bostonuniversity: bostonUniversityData as SchoolData,
  caltech: caltechData as SchoolData,
  cmu: cmuData as SchoolData,
  columbia: columbiaData as SchoolData,
  cornell: cornellData as SchoolData,
  dartmouth: dartmouthData as SchoolData,
  duke: dukeData as SchoolData,
  emory: emoryData as SchoolData,
  georgiatech: georgiaTechData as SchoolData,
  harvard: harvardData as SchoolData,
  johnshopkins: johnsHopkinsData as SchoolData,
  princeton: princetonData as SchoolData,
  stanford: stanfordData as SchoolData,
  ucla: uclaData as SchoolData,
  ucberkeley: ucberkeleyData as SchoolData,
  ucdavis: ucdavisData as SchoolData,
  ucsandiego: ucsanDiegoData as SchoolData,
  uci: uciData as SchoolData,
  uchicago: uchicagoData as SchoolData,
  uiuc: uiucData as SchoolData,
  uncchapelhill: uncChapelHillData as SchoolData,
  umich: umichData as SchoolData,
  upenn: upennData as SchoolData,
  usc: uscData as SchoolData,
  uwmadison: uwmadisonData as SchoolData,
  uwashington: uwashingtonData as SchoolData,
  utexasaustin: utexasaustinData as SchoolData,
  uva: uvaData as SchoolData,
  vanderbilt: vanderbiltData as SchoolData,
  yale: yaleData as SchoolData,
  mit: mitData as SchoolData,
  northeastern: northeasternData as SchoolData,
  notredame: notreDameData as SchoolData,
  nyu: nyuData as SchoolData,
  northwestern: northwesternData as SchoolData,
  rice: riceData as SchoolData,
  purdue: purdueData as SchoolData,
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
