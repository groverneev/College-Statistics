import { SchoolData } from "@/lib/types";
import { getLatestYear } from "@/utils/dataHelpers";

import bostonCollegeData from "./bostoncollege.json";
import bostonUniversityData from "./bostonuniversity.json";
import brownData from "./brown.json";
import caltechData from "./caltech.json";
import caseWesternReserveData from "./casewesternreserve.json";
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
import miamiData from "./miami.json";
import mitData from "./mit.json";
import northeasternData from "./northeastern.json";
import northwesternData from "./northwestern.json";
import notreDameData from "./notredame.json";
import nyuData from "./nyu.json";
import ohioStateData from "./ohiostate.json";
import pennStateData from "./pennstate.json";
import princetonData from "./princeton.json";
import purdueData from "./purdue.json";
import riceData from "./rice.json";
import rochesterData from "./rochester.json";
import rutgersNewBrunswickData from "./rutgersnewbrunswick.json";
import stanfordData from "./stanford.json";
import texasAmData from "./texasam.json";
import tuftsData from "./tufts.json";
import tulaneData from "./tulane.json";
import ucberkeleyData from "./ucberkeley.json";
import ucdavisData from "./ucdavis.json";
import uchicagoData from "./uchicago.json";
import uciData from "./uci.json";
import uclaData from "./ucla.json";
import ucmercedData from "./ucmerced.json";
import ucSantaCruzData from "./ucsantacruz.json";
import ucsanDiegoData from "./ucsandiego.json";
import ucsbData from "./ucsb.json";
import ucriversideData from "./ucriverside.json";
import ufloridaData from "./uflorida.json";
import uiucData from "./uiuc.json";
import umdData from "./umd.json";
import umichData from "./umich.json";
import uncChapelHillData from "./uncchapelhill.json";
import universityPittsburghData from "./universitypittsburgh.json";
import upennData from "./upenn.json";
import uscData from "./usc.json";
import utexasaustinData from "./utexasaustin.json";
import uvaData from "./uva.json";
import uwashingtonData from "./uwashington.json";
import uwmadisonData from "./uwmadison.json";
import vanderbiltData from "./vanderbilt.json";
import wakeForestData from "./wakeforest.json";
import washuData from "./washu.json";
import williamAndMaryData from "./williamandmary.json";
import yaleData from "./yale.json";

export interface SearchableSchool {
  name: string;
  slug: string;
  acceptanceRate: number;
}

type SchoolMetadata = {
  aliases?: string[];
  color: string;
  featured?: boolean;
};

export const allSchools: SchoolData[] = [
  bostonCollegeData as SchoolData,
  bostonUniversityData as SchoolData,
  brownData as SchoolData,
  caltechData as SchoolData,
  caseWesternReserveData as SchoolData,
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
  miamiData as SchoolData,
  northeasternData as SchoolData,
  northwesternData as SchoolData,
  notreDameData as SchoolData,
  nyuData as SchoolData,
  ohioStateData as SchoolData,
  pennStateData as SchoolData,
  princetonData as SchoolData,
  riceData as SchoolData,
  rochesterData as SchoolData,
  purdueData as SchoolData,
  rutgersNewBrunswickData as SchoolData,
  stanfordData as SchoolData,
  texasAmData as SchoolData,
  tuftsData as SchoolData,
  tulaneData as SchoolData,
  uclaData as SchoolData,
  ucberkeleyData as SchoolData,
  ucdavisData as SchoolData,
  ucsbData as SchoolData,
  ucSantaCruzData as SchoolData,
  ucsanDiegoData as SchoolData,
  uciData as SchoolData,
  ucmercedData as SchoolData,
  ucriversideData as SchoolData,
  uchicagoData as SchoolData,
  ufloridaData as SchoolData,
  uiucData as SchoolData,
  umdData as SchoolData,
  uncChapelHillData as SchoolData,
  umichData as SchoolData,
  upennData as SchoolData,
  universityPittsburghData as SchoolData,
  uscData as SchoolData,
  uwmadisonData as SchoolData,
  uwashingtonData as SchoolData,
  utexasaustinData as SchoolData,
  uvaData as SchoolData,
  vanderbiltData as SchoolData,
  wakeForestData as SchoolData,
  washuData as SchoolData,
  williamAndMaryData as SchoolData,
  yaleData as SchoolData,
];

export const SCHOOL_METADATA: Record<string, SchoolMetadata> = {
  bostoncollege: { aliases: ["BC", "Boston College"], color: "#98002E" },
  bostonuniversity: {
    aliases: ["BU", "Boston U", "Boston University"],
    color: "#CC0000",
  },
  brown: { aliases: ["Brown"], color: "#4E3629" },
  caltech: {
    aliases: ["Caltech", "Cal Tech", "CIT"],
    color: "#FF6C0C",
  },
  casewesternreserve: {
    aliases: [
      "Case Western",
      "Case Western Reserve",
      "Case Western Reserve University",
      "CWRU",
    ],
    color: "#0C2340",
  },
  cmu: {
    aliases: ["CMU", "Carnegie Mellon", "Carnegie-Mellon"],
    color: "#C41230",
  },
  columbia: { aliases: ["Columbia"], color: "#1D4F91" },
  cornell: { aliases: ["Cornell"], color: "#B31B1B" },
  dartmouth: { aliases: ["Dartmouth"], color: "#00693E" },
  duke: { aliases: ["Duke"], color: "#012169" },
  emory: { aliases: ["Emory", "Emory University"], color: "#012169" },
  georgiatech: {
    aliases: [
      "Georgia Tech",
      "Georgia Institute of Technology",
      "Georgia Tech University",
      "GaTech",
      "GT",
    ],
    color: "#B3A369",
  },
  georgetown: {
    aliases: ["Georgetown", "Georgetown University", "GU"],
    color: "#041E42",
  },
  harvard: {
    aliases: ["Harvard"],
    color: "#A51C30",
    featured: true,
  },
  johnshopkins: {
    aliases: ["JHU", "Johns Hopkins", "Johns Hopkins University", "Hopkins"],
    color: "#002D72",
  },
  miami: {
    aliases: ["Miami", "University of Miami", "UM", "The U"],
    color: "#F47321",
  },
  mit: {
    aliases: ["MIT", "Massachusetts Institute of Technology"],
    color: "#A31F34",
    featured: true,
  },
  northeastern: {
    aliases: ["Northeastern", "Northeastern University", "NEU"],
    color: "#C8102E",
  },
  northwestern: {
    aliases: ["NU", "Northwestern"],
    color: "#4E2A84",
  },
  notredame: {
    aliases: ["Notre Dame", "University of Notre Dame", "ND"],
    color: "#0C2340",
  },
  nyu: { aliases: ["NYU", "New York University"], color: "#57068C" },
  ohiostate: {
    aliases: [
      "OSU",
      "Ohio State",
      "Ohio State University",
      "The Ohio State University",
      "tOSU",
    ],
    color: "#BB0000",
  },
  pennstate: {
    aliases: [
      "Penn State",
      "Penn State University",
      "Pennsylvania State University",
      "PSU",
    ],
    color: "#001E44",
  },
  princeton: { aliases: ["Princeton"], color: "#E77500" },
  purdue: {
    aliases: ["Purdue", "Purdue University", "Purdue West Lafayette"],
    color: "#CFB991",
  },
  rice: {
    aliases: ["Rice", "Rice University", "William Marsh Rice University"],
    color: "#00205B",
  },
  rochester: {
    aliases: ["Rochester", "University of Rochester", "UR"],
    color: "#00467F",
  },
  rutgersnewbrunswick: {
    aliases: [
      "Rutgers",
      "Rutgers New Brunswick",
      "Rutgers-New Brunswick",
      "RU",
    ],
    color: "#CC0033",
  },
  stanford: {
    aliases: ["Stanford"],
    color: "#8C1515",
    featured: true,
  },
  texasam: {
    aliases: [
      "Texas A&M",
      "Texas A and M",
      "Texas A & M",
      "Texas A&M University",
      "TAMU",
      "A&M",
    ],
    color: "#500000",
  },
  tufts: { aliases: ["Tufts", "Tufts University"], color: "#3E8EDE" },
  tulane: { aliases: ["Tulane", "Tulane University"], color: "#006747" },
  ucberkeley: {
    aliases: [
      "UC Berkeley",
      "Cal",
      "Berkeley",
      "University of California Berkeley",
    ],
    color: "#003262",
  },
  ucdavis: {
    aliases: [
      "UC Davis",
      "University of California Davis",
      "University of California, Davis",
      "Davis",
    ],
    color: "#022851",
  },
  ucmerced: {
    aliases: [
      "UC Merced",
      "University of California Merced",
      "University of California, Merced",
      "Merced",
    ],
    color: "#0F2D52",
  },
  uchicago: {
    aliases: ["UChicago", "University of Chicago", "Chicago"],
    color: "#800000",
  },
  uci: {
    aliases: [
      "UCI",
      "UC Irvine",
      "University of California Irvine",
      "University of California, Irvine",
      "Irvine",
    ],
    color: "#0064A4",
  },
  ucla: {
    aliases: [
      "UCLA",
      "University of California Los Angeles",
      "UC Los Angeles",
    ],
    color: "#2774AE",
  },
  ucsandiego: {
    aliases: [
      "UCSD",
      "UC San Diego",
      "University of California San Diego",
      "University of California, San Diego",
      "San Diego",
    ],
    color: "#182B49",
  },
  ucsb: {
    aliases: [
      "UCSB",
      "UC Santa Barbara",
      "University of California Santa Barbara",
      "University of California, Santa Barbara",
      "Santa Barbara",
    ],
    color: "#003660",
  },
  ucsantacruz: {
    aliases: [
      "UCSC",
      "UC Santa Cruz",
      "University of California Santa Cruz",
      "University of California, Santa Cruz",
      "Santa Cruz",
    ],
    color: "#003C6C",
  },
  ucriverside: {
    aliases: [
      "UCR",
      "UC Riverside",
      "University of California Riverside",
      "University of California, Riverside",
      "Riverside",
    ],
    color: "#003DA5",
  },
  uflorida: {
    aliases: ["UF", "UFlorida", "U of F", "Florida", "University of Florida"],
    color: "#0021A5",
  },
  uiuc: {
    aliases: [
      "UIUC",
      "University of Illinois Urbana-Champaign",
      "University of Illinois",
      "Illinois",
      "U of I",
      "Urbana-Champaign",
    ],
    color: "#13294B",
  },
  umd: {
    aliases: [
      "UMD",
      "Maryland",
      "College Park",
      "University of Maryland",
      "University of Maryland College Park",
      "University of Maryland, College Park",
    ],
    color: "#E21833",
  },
  umich: {
    aliases: [
      "UMich",
      "U-M",
      "Michigan",
      "University of Michigan",
      "University of Michigan Ann Arbor",
      "UM Ann Arbor",
    ],
    color: "#00274C",
  },
  uncchapelhill: {
    aliases: [
      "UNC",
      "UNC Chapel Hill",
      "UNC-Chapel Hill",
      "Carolina",
      "University of North Carolina",
      "University of North Carolina at Chapel Hill",
    ],
    color: "#4B9CD3",
  },
  universitypittsburgh: {
    aliases: [
      "Pitt",
      "University of Pittsburgh",
      "Pittsburgh",
      "Pittsburgh Campus",
      "UPitt",
      "U Pitt",
    ],
    color: "#003594",
  },
  upenn: {
    aliases: ["UPenn", "Penn", "U Penn", "University of Pennsylvania"],
    color: "#011F5B",
  },
  usc: {
    aliases: ["USC", "Southern Cal", "University of Southern California"],
    color: "#990000",
  },
  utexasaustin: {
    aliases: [
      "UT Austin",
      "UTexasAustin",
      "UTexas",
      "University of Texas at Austin",
      "University of Texas Austin",
    ],
    color: "#BF5700",
  },
  uva: {
    aliases: ["UVA", "University of Virginia", "Virginia", "U. Virginia"],
    color: "#232D4B",
  },
  uwashington: {
    aliases: [],
    color: "#4B2E83",
  },
  uwmadison: {
    aliases: [
      "UW Madison",
      "UW-Madison",
      "Wisconsin",
      "Wisconsin Madison",
      "University of Wisconsin",
      "University of Wisconsin Madison",
      "University of Wisconsin-Madison",
    ],
    color: "#C5050C",
  },
  vanderbilt: {
    aliases: ["Vanderbilt", "Vandy", "Vanderbilt University"],
    color: "#866D4B",
  },
  wakeforest: {
    aliases: ["Wake", "Wake Forest", "Wake Forest University"],
    color: "#9E7E38",
  },
  washu: {
    aliases: [
      "WashU",
      "Wash U",
      "WUSTL",
      "Washington University",
      "Washington University in St. Louis",
      "Washington University in St Louis",
    ],
    color: "#A51417",
  },
  williamandmary: {
    aliases: [
      "William and Mary",
      "William & Mary",
      "W&M",
      "William Mary",
    ],
    color: "#115740",
  },
  yale: { aliases: ["Yale"], color: "#00356B" },
};

export const schoolDataMap: Record<string, SchoolData> = Object.fromEntries(
  allSchools.map((school) => [school.slug, school])
);

export const SCHOOL_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(SCHOOL_METADATA).map(([slug, metadata]) => [slug, metadata.color])
);

export const SCHOOL_ALIASES: Record<string, string[]> = Object.fromEntries(
  Object.entries(SCHOOL_METADATA).map(([slug, metadata]) => [slug, metadata.aliases ?? []])
);

export const FEATURED_SCHOOL_SLUGS = Object.entries(SCHOOL_METADATA)
  .filter(([, metadata]) => metadata.featured)
  .map(([slug]) => slug);

export const featuredSchools: SchoolData[] = FEATURED_SCHOOL_SLUGS.map(
  (slug) => schoolDataMap[slug]
).filter((school): school is SchoolData => Boolean(school));

export const availableSchoolSlugs = allSchools.map((school) => school.slug);

export const searchableSchools: SearchableSchool[] = allSchools.map((school) => {
  const latestYear = getLatestYear(school);
  const latestData = latestYear ? school.years[latestYear] : null;

  return {
    name: school.name,
    slug: school.slug,
    acceptanceRate: latestData?.admissions.acceptanceRate ?? 0,
  };
});

export function getSchoolColor(slug: string): string {
  return SCHOOL_COLORS[slug] ?? "#4B5563";
}
