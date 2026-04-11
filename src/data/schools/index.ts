import { SchoolData } from "@/lib/types";

import bostonUniversityData from "./bostonuniversity.json";
import brownData from "./brown.json";
import caltechData from "./caltech.json";
import cmuData from "./cmu.json";
import columbiaData from "./columbia.json";
import cornellData from "./cornell.json";
import dartmouthData from "./dartmouth.json";
import dukeData from "./duke.json";
import emoryData from "./emory.json";
import georgiaTechData from "./georgiatech.json";
import georgetownData from "./georgetown.json";
import harvardData from "./harvard.json";
import johnsHopkinsData from "./johnshopkins.json";
import mitData from "./mit.json";
import northeasternData from "./northeastern.json";
import northwesternData from "./northwestern.json";
import notreDameData from "./notredame.json";
import nyuData from "./nyu.json";
import princetonData from "./princeton.json";
import purdueData from "./purdue.json";
import riceData from "./rice.json";
import stanfordData from "./stanford.json";
import tuftsData from "./tufts.json";
import uclaData from "./ucla.json";
import ucberkeleyData from "./ucberkeley.json";
import ucdavisData from "./ucdavis.json";
import uchicagoData from "./uchicago.json";
import uciData from "./uci.json";
import ucsanDiegoData from "./ucsandiego.json";
import uiucData from "./uiuc.json";
import umichData from "./umich.json";
import uncChapelHillData from "./uncchapelhill.json";
import upennData from "./upenn.json";
import uscData from "./usc.json";
import utexasaustinData from "./utexasaustin.json";
import uvaData from "./uva.json";
import uwashingtonData from "./uwashington.json";
import uwmadisonData from "./uwmadison.json";
import vanderbiltData from "./vanderbilt.json";
import yaleData from "./yale.json";

export interface SearchableSchool {
  name: string;
  slug: string;
  acceptanceRate: number;
}

export const allSchools: SchoolData[] = [
  bostonUniversityData as SchoolData,
  brownData as SchoolData,
  caltechData as SchoolData,
  cmuData as SchoolData,
  columbiaData as SchoolData,
  cornellData as SchoolData,
  dartmouthData as SchoolData,
  dukeData as SchoolData,
  emoryData as SchoolData,
  georgiaTechData as SchoolData,
  georgetownData as SchoolData,
  harvardData as SchoolData,
  johnsHopkinsData as SchoolData,
  mitData as SchoolData,
  northeasternData as SchoolData,
  northwesternData as SchoolData,
  notreDameData as SchoolData,
  nyuData as SchoolData,
  princetonData as SchoolData,
  riceData as SchoolData,
  purdueData as SchoolData,
  stanfordData as SchoolData,
  tuftsData as SchoolData,
  uclaData as SchoolData,
  ucberkeleyData as SchoolData,
  ucdavisData as SchoolData,
  ucsanDiegoData as SchoolData,
  uciData as SchoolData,
  uchicagoData as SchoolData,
  uiucData as SchoolData,
  uncChapelHillData as SchoolData,
  umichData as SchoolData,
  upennData as SchoolData,
  uscData as SchoolData,
  uwmadisonData as SchoolData,
  uwashingtonData as SchoolData,
  utexasaustinData as SchoolData,
  uvaData as SchoolData,
  vanderbiltData as SchoolData,
  yaleData as SchoolData,
];

export const schoolDataMap: Record<string, SchoolData> = Object.fromEntries(
  allSchools.map((school) => [school.slug, school])
);

export const availableSchoolSlugs = allSchools.map((school) => school.slug);

export const searchableSchools: SearchableSchool[] = allSchools.map((school) => {
  const years = Object.keys(school.years).sort();
  const latestYear = years[years.length - 1];
  const latestData = school.years[latestYear];

  return {
    name: school.name,
    slug: school.slug,
    acceptanceRate: latestData.admissions.acceptanceRate,
  };
});
