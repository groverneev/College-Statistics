import type { SchoolData } from "@/lib/types";
import { getLatestYear, getSchoolYearRange, getSortedYears } from "@/utils/dataHelpers";

import bostonCollegeData from "./bostoncollege.json";
import bostonUniversityData from "./bostonuniversity.json";
import bowdoincollegeData from "./bowdoincollege.json";
import brownData from "./brown.json";
import caltechData from "./caltech.json";
import cmuData from "./cmu.json";
import caseWesternReserveData from "./casewesternreserve.json";
import columbiaData from "./columbia.json";
import cornellData from "./cornell.json";
import dartmouthData from "./dartmouth.json";
import dukeData from "./duke.json";
import emoryData from "./emory.json";
import georgetownData from "./georgetown.json";
import georgiaTechData from "./georgiatech.json";
import harvardData from "./harvard.json";
import johnsHopkinsData from "./johnshopkins.json";
import mitData from "./mit.json";
import nyuData from "./nyu.json";
import northeasternData from "./northeastern.json";
import northwesternData from "./northwestern.json";
import pennStateData from "./pennstate.json";
import pomonacollegeData from "./pomonacollege.json";
import princetonData from "./princeton.json";
import purdueData from "./purdue.json";
import riceData from "./rice.json";
import rutgersNewBrunswickData from "./rutgersnewbrunswick.json";
import stanfordData from "./stanford.json";
import swarthmorecollegeData from "./swarthmorecollege.json";
import texasAmData from "./texasam.json";
import ohioStateData from "./ohiostate.json";
import utexasaustinData from "./utexasaustin.json";
import tuftsData from "./tufts.json";
import tulaneData from "./tulane.json";
import uclaData from "./ucla.json";
import ucberkeleyData from "./ucberkeley.json";
import ucdavisData from "./ucdavis.json";
import uciData from "./uci.json";
import ucmercedData from "./ucmerced.json";
import ucriversideData from "./ucriverside.json";
import ucsanDiegoData from "./ucsandiego.json";
import ucsbData from "./ucsb.json";
import ucSantaCruzData from "./ucsantacruz.json";
import uchicagoData from "./uchicago.json";
import ufloridaData from "./uflorida.json";
import uiucData from "./uiuc.json";
import umdData from "./umd.json";
import miamiData from "./miami.json";
import umichData from "./umich.json";
import uncChapelHillData from "./uncchapelhill.json";
import notreDameData from "./notredame.json";
import upennData from "./upenn.json";
import universityPittsburghData from "./universitypittsburgh.json";
import rochesterData from "./rochester.json";
import uscData from "./usc.json";
import uvaData from "./uva.json";
import uwashingtonData from "./uwashington.json";
import uwmadisonData from "./uwmadison.json";
import vanderbiltData from "./vanderbilt.json";
import wakeForestData from "./wakeforest.json";
import washuData from "./washu.json";
import williamAndMaryData from "./williamandmary.json";
import yaleData from "./yale.json";
import amherstcollegeData from "./amherstcollege.json";
import williamscollegeData from "./williamscollege.json";
import claremontmckennaData from "./claremontmckenna.json";
import harveymuddData from "./harveymudd.json";
import universityofgeorgiaData from "./universityofgeorgia.json";
import santaclaraData from "./santaclara.json";
import virginiatechData from "./virginiatech.json";
import lehighData from "./lehigh.json";
import brandeisData from "./brandeis.json";
import villanovaData from "./villanova.json";
import floridastateData from "./floridastate.json";
import umassamherstData from "./umassamherst.json";
import universityofminnesotaData from "./universityofminnesota.json";
import michiganstateData from "./michiganstate.json";
import gwuData from "./gwu.json";
import stonybrookData from "./stonybrook.json";
import stevensData from "./stevens.json";
import syracuseuniversityData from "./syracuseuniversity.json";
import howardData from "./howard.json";
import indianabloomingtonData from "./indianabloomington.json";
import rensselaerData from "./rensselaer.json";
import binghamtonData from "./binghamton.json";
import ncstateData from "./ncstate.json";
import vassarData from "./vassar.json";
import wellesleyData from "./wellesley.json";
import hamiltoncollegeData from "./hamiltoncollege.json";
import washingtonandleeData from "./washingtonandlee.json";
import wesleyanData from "./wesleyan.json";
import carletoncollegeData from "./carletoncollege.json";
import davidsoncollegeData from "./davidsoncollege.json";
import middleburycollegeData from "./middleburycollege.json";
import barnardcollegeData from "./barnardcollege.json";
import colbycollegeData from "./colbycollege.json";
import grinnellcollegeData from "./grinnellcollege.json";
import wpiData from "./wpi.json";
import uconnData from "./uconn.json";
import universityofrichmondData from "./universityofrichmond.json";
import colgateData from "./colgate.json";
import reedcollegeData from "./reedcollege.json";
import bucknellData from "./bucknell.json";
import lafayetteData from "./lafayette.json";
import macalesterData from "./macalester.json";
import batescollegeData from "./batescollege.json";
import brynmawrData from "./brynmawr.json";
import mountholyokeData from "./mountholyoke.json";
import occidentalData from "./occidental.json";
import haverfordcollegeData from "./haverfordcollege.json";
import kenyoncollegeData from "./kenyoncollege.json";
import oberlincollegeData from "./oberlincollege.json";
import universityofdelawareData from "./universityofdelaware.json";

export interface SearchableSchool {
  name: string;
  slug: string;
  acceptanceRate: number;
  aliases: string[];
}

export type SchoolControl = "public" | "private";

type SchoolMetadata = {
  aliases?: string[];
  color: string;
  /** Two-letter postal code of the main campus (DC included). */
  state: string;
  control: SchoolControl;
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
  pomonacollegeData as SchoolData,
  swarthmorecollegeData as SchoolData,
  bowdoincollegeData as SchoolData,
  amherstcollegeData as SchoolData,
  williamscollegeData as SchoolData,
  claremontmckennaData as SchoolData,
  harveymuddData as SchoolData,
  universityofgeorgiaData as SchoolData,
  santaclaraData as SchoolData,
  virginiatechData as SchoolData,
  lehighData as SchoolData,
  brandeisData as SchoolData,
  villanovaData as SchoolData,
  floridastateData as SchoolData,
  umassamherstData as SchoolData,
  universityofminnesotaData as SchoolData,
  michiganstateData as SchoolData,
  gwuData as SchoolData,
  stonybrookData as SchoolData,
  stevensData as SchoolData,
  syracuseuniversityData as SchoolData,
  howardData as SchoolData,
  indianabloomingtonData as SchoolData,
  rensselaerData as SchoolData,
  binghamtonData as SchoolData,
  ncstateData as SchoolData,
  vassarData as SchoolData,
  wellesleyData as SchoolData,
  hamiltoncollegeData as SchoolData,
  washingtonandleeData as SchoolData,
  wesleyanData as SchoolData,
  carletoncollegeData as SchoolData,
  davidsoncollegeData as SchoolData,
  middleburycollegeData as SchoolData,
  barnardcollegeData as SchoolData,
  colbycollegeData as SchoolData,
  grinnellcollegeData as SchoolData,
  wpiData as SchoolData,
  uconnData as SchoolData,
  universityofrichmondData as SchoolData,
  colgateData as SchoolData,
  reedcollegeData as SchoolData,
  bucknellData as SchoolData,
  lafayetteData as SchoolData,
  macalesterData as SchoolData,
  batescollegeData as SchoolData,
  brynmawrData as SchoolData,
  mountholyokeData as SchoolData,
  occidentalData as SchoolData,
  haverfordcollegeData as SchoolData,
  kenyoncollegeData as SchoolData,
  oberlincollegeData as SchoolData,
  universityofdelawareData as SchoolData,
];

export const SCHOOL_METADATA: Record<string, SchoolMetadata> = {
  bostoncollege: {
    aliases: ["BC", "Boston College"],
    state: "MA",
    control: "private",
    color: "#98002E",
  },
  bostonuniversity: {
    aliases: ["BU", "Boston U", "Boston University"],
    state: "MA",
    control: "private",
    color: "#CC0000",
  },
  brown: { aliases: ["Brown"], state: "RI", control: "private", color: "#4E3629" },
  caltech: {
    aliases: ["Caltech", "Cal Tech", "CIT"],
    state: "CA",
    control: "private",
    color: "#FF6C0C",
  },
  casewesternreserve: {
    aliases: ["Case Western", "Case Western Reserve", "Case Western Reserve University", "CWRU"],
    state: "OH",
    control: "private",
    color: "#0C2340",
  },
  cmu: {
    aliases: ["CMU", "Carnegie Mellon", "Carnegie-Mellon"],
    state: "PA",
    control: "private",
    color: "#C41230",
  },
  columbia: { aliases: ["Columbia"], state: "NY", control: "private", color: "#1D4F91" },
  cornell: { aliases: ["Cornell"], state: "NY", control: "private", color: "#B31B1B" },
  dartmouth: { aliases: ["Dartmouth"], state: "NH", control: "private", color: "#00693E" },
  duke: { aliases: ["Duke"], state: "NC", control: "private", color: "#012169" },
  emory: {
    aliases: ["Emory", "Emory University"],
    state: "GA",
    control: "private",
    color: "#012169",
  },
  georgiatech: {
    aliases: [
      "Georgia Tech",
      "Georgia Institute of Technology",
      "Georgia Tech University",
      "GaTech",
      "GT",
    ],
    state: "GA",
    control: "public",
    color: "#B3A369",
  },
  georgetown: {
    aliases: ["Georgetown", "Georgetown University", "GU"],
    state: "DC",
    control: "private",
    color: "#041E42",
  },
  harvard: {
    aliases: ["Harvard"],
    state: "MA",
    control: "private",
    color: "#A51C30",
    featured: true,
  },
  johnshopkins: {
    aliases: ["JHU", "Johns Hopkins", "Johns Hopkins University", "Hopkins"],
    state: "MD",
    control: "private",
    color: "#002D72",
  },
  miami: {
    aliases: ["Miami", "University of Miami", "UM", "The U"],
    state: "FL",
    control: "private",
    color: "#F47321",
  },
  mit: {
    aliases: ["MIT", "Massachusetts Institute of Technology"],
    state: "MA",
    control: "private",
    color: "#A31F34",
    featured: true,
  },
  northeastern: {
    aliases: ["Northeastern", "Northeastern University", "NEU"],
    state: "MA",
    control: "private",
    color: "#C8102E",
  },
  northwestern: {
    aliases: ["NU", "Northwestern"],
    state: "IL",
    control: "private",
    color: "#4E2A84",
  },
  notredame: {
    aliases: ["Notre Dame", "University of Notre Dame", "ND"],
    state: "IN",
    control: "private",
    color: "#0C2340",
  },
  nyu: {
    aliases: ["NYU", "New York University"],
    state: "NY",
    control: "private",
    color: "#57068C",
  },
  ohiostate: {
    aliases: ["OSU", "Ohio State", "Ohio State University", "The Ohio State University", "tOSU"],
    state: "OH",
    control: "public",
    color: "#BB0000",
  },
  pennstate: {
    aliases: ["Penn State", "Penn State University", "Pennsylvania State University", "PSU"],
    state: "PA",
    control: "public",
    color: "#001E44",
  },
  princeton: { aliases: ["Princeton"], state: "NJ", control: "private", color: "#E77500" },
  purdue: {
    aliases: ["Purdue", "Purdue University", "Purdue West Lafayette"],
    state: "IN",
    control: "public",
    color: "#CFB991",
  },
  rice: {
    aliases: ["Rice", "Rice University", "William Marsh Rice University"],
    state: "TX",
    control: "private",
    color: "#00205B",
  },
  rochester: {
    aliases: ["Rochester", "University of Rochester", "UR"],
    state: "NY",
    control: "private",
    color: "#00467F",
  },
  rutgersnewbrunswick: {
    aliases: ["Rutgers", "Rutgers New Brunswick", "Rutgers-New Brunswick", "RU"],
    state: "NJ",
    control: "public",
    color: "#CC0033",
  },
  stanford: {
    aliases: ["Stanford"],
    state: "CA",
    control: "private",
    color: "#8C1515",
    featured: true,
  },
  texasam: {
    aliases: ["Texas A&M", "Texas A and M", "Texas A & M", "Texas A&M University", "TAMU", "A&M"],
    state: "TX",
    control: "public",
    color: "#500000",
  },
  tufts: {
    aliases: ["Tufts", "Tufts University"],
    state: "MA",
    control: "private",
    color: "#3E8EDE",
  },
  tulane: {
    aliases: ["Tulane", "Tulane University"],
    state: "LA",
    control: "private",
    color: "#006747",
  },
  ucberkeley: {
    aliases: ["UC Berkeley", "Cal", "Berkeley", "University of California Berkeley"],
    state: "CA",
    control: "public",
    color: "#003262",
  },
  ucdavis: {
    aliases: [
      "UC Davis",
      "University of California Davis",
      "University of California, Davis",
      "Davis",
    ],
    state: "CA",
    control: "public",
    color: "#022851",
  },
  ucmerced: {
    aliases: [
      "UC Merced",
      "University of California Merced",
      "University of California, Merced",
      "Merced",
    ],
    state: "CA",
    control: "public",
    color: "#0F2D52",
  },
  uchicago: {
    aliases: ["UChicago", "University of Chicago", "Chicago"],
    state: "IL",
    control: "private",
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
    state: "CA",
    control: "public",
    color: "#0064A4",
  },
  ucla: {
    aliases: ["UCLA", "University of California Los Angeles", "UC Los Angeles"],
    state: "CA",
    control: "public",
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
    state: "CA",
    control: "public",
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
    state: "CA",
    control: "public",
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
    state: "CA",
    control: "public",
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
    state: "CA",
    control: "public",
    color: "#003DA5",
  },
  uflorida: {
    aliases: ["UF", "UFlorida", "U of F", "Florida", "University of Florida"],
    state: "FL",
    control: "public",
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
    state: "IL",
    control: "public",
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
    state: "MD",
    control: "public",
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
    state: "MI",
    control: "public",
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
    state: "NC",
    control: "public",
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
    state: "PA",
    control: "public",
    color: "#003594",
  },
  upenn: {
    aliases: ["UPenn", "Penn", "U Penn", "University of Pennsylvania"],
    state: "PA",
    control: "private",
    color: "#011F5B",
  },
  usc: {
    aliases: ["USC", "Southern Cal", "University of Southern California"],
    state: "CA",
    control: "private",
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
    state: "TX",
    control: "public",
    color: "#BF5700",
  },
  uva: {
    aliases: ["UVA", "University of Virginia", "Virginia", "U. Virginia"],
    state: "VA",
    control: "public",
    color: "#232D4B",
  },
  uwashington: {
    aliases: [],
    state: "WA",
    control: "public",
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
    state: "WI",
    control: "public",
    color: "#C5050C",
  },
  vanderbilt: {
    aliases: ["Vanderbilt", "Vandy", "Vanderbilt University"],
    state: "TN",
    control: "private",
    color: "#866D4B",
  },
  wakeforest: {
    aliases: ["Wake", "Wake Forest", "Wake Forest University"],
    state: "NC",
    control: "private",
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
    state: "MO",
    control: "private",
    color: "#A51417",
  },
  williamandmary: {
    aliases: ["William and Mary", "William & Mary", "W&M", "William Mary"],
    state: "VA",
    control: "public",
    color: "#115740",
  },
  yale: { aliases: ["Yale"], state: "CT", control: "private", color: "#00356B" },
  amherstcollege: {
    aliases: ["Amherst", "Amherst College"],
    state: "MA",
    control: "private",
    color: "#3F1F69",
  },
  williamscollege: {
    aliases: ["Williams", "Williams College"],
    state: "MA",
    control: "private",
    color: "#500082",
  },
  claremontmckenna: {
    aliases: ["CMC", "Claremont McKenna", "Claremont McKenna College", "Claremont"],
    state: "CA",
    control: "private",
    color: "#981A31",
  },
  harveymudd: {
    aliases: ["Harvey Mudd", "Mudd", "HMC", "Harvey Mudd College"],
    state: "CA",
    control: "private",
    color: "#FDB913",
  },
  universityofgeorgia: {
    aliases: ["UGA", "Georgia", "University of Georgia", "Georgia Bulldogs"],
    state: "GA",
    control: "public",
    color: "#BA0C2F",
  },
  santaclara: {
    aliases: ["SCU", "Santa Clara"],
    state: "CA",
    control: "private",
    color: "#B30838",
  },
  virginiatech: {
    aliases: ["Virginia Tech", "VT", "Virginia Polytechnic Institute and State University"],
    state: "VA",
    control: "public",
    color: "#861F41",
  },
  lehigh: {
    aliases: ["Lehigh", "LU"],
    state: "PA",
    control: "private",
    color: "#502D0E",
  },
  brandeis: {
    aliases: ["Brandeis", "Brandeis U"],
    state: "MA",
    control: "private",
    color: "#003478",
  },
  villanova: {
    aliases: ["Villanova", "Nova", "VU"],
    state: "PA",
    control: "private",
    color: "#002664",
  },
  floridastate: {
    aliases: ["FSU", "Florida State", "Florida State University", "Seminoles"],
    state: "FL",
    control: "public",
    color: "#782F40",
  },
  umassamherst: {
    aliases: ["UMass Amherst", "UMass", "University of Massachusetts", "Massachusetts Amherst"],
    state: "MA",
    control: "public",
    color: "#840028",
  },
  universityofminnesota: {
    aliases: ["University of Minnesota", "UMN", "UMTC", "Minnesota", "Twin Cities", "U of M"],
    state: "MN",
    control: "public",
    color: "#7A0019",
  },
  michiganstate: {
    aliases: ["Michigan State", "MSU", "Spartans"],
    state: "MI",
    control: "public",
    color: "#18453B",
  },
  gwu: {
    aliases: ["George Washington", "GWU", "GW"],
    state: "DC",
    control: "private",
    color: "#033C5A",
  },
  stonybrook: {
    aliases: ["Stony Brook", "SBU", "SUNY Stony Brook"],
    state: "NY",
    control: "public",
    color: "#990000",
  },
  stevens: {
    aliases: ["Stevens", "SIT", "Stevens Tech"],
    state: "NJ",
    control: "private",
    color: "#A32638",
  },
  syracuseuniversity: {
    aliases: ["Syracuse", "SU", "Cuse"],
    state: "NY",
    control: "private",
    color: "#F76900",
  },
  howard: {
    aliases: ["Howard", "HU"],
    state: "DC",
    control: "private",
    color: "#003A63",
  },
  indianabloomington: {
    aliases: ["Indiana University", "IU Bloomington", "IU", "Indiana"],
    state: "IN",
    control: "public",
    color: "#990000",
  },
  rensselaer: {
    aliases: ["RPI", "Rensselaer", "Rensselaer Polytechnic"],
    state: "NY",
    control: "private",
    color: "#D6001C",
  },
  binghamton: {
    aliases: [
      "Binghamton",
      "SUNY Binghamton",
      "State University of New York at Binghamton",
      "Bing",
    ],
    state: "NY",
    control: "public",
    color: "#005A43",
  },
  ncstate: {
    aliases: ["NC State", "NCSU", "North Carolina State"],
    state: "NC",
    control: "public",
    color: "#CC0000",
  },
  vassar: {
    aliases: ["Vassar", "Vassar College"],
    state: "NY",
    control: "private",
    color: "#A41E35",
  },
  wellesley: {
    aliases: ["Wellesley", "WC"],
    state: "MA",
    control: "private",
    color: "#002F6C",
  },
  hamiltoncollege: {
    aliases: ["Hamilton", "Hamilton College"],
    state: "NY",
    control: "private",
    color: "#002F86",
  },
  washingtonandlee: {
    aliases: ["W&L", "WLU", "Washington and Lee"],
    state: "VA",
    control: "private",
    color: "#003087",
  },
  wesleyan: {
    aliases: ["Wesleyan", "Wes"],
    state: "CT",
    control: "private",
    color: "#D72121",
  },
  carletoncollege: {
    aliases: ["Carleton", "Carleton College", "Carl"],
    state: "MN",
    control: "private",
    color: "#003069",
  },
  davidsoncollege: {
    aliases: ["Davidson"],
    state: "NC",
    control: "private",
    color: "#D42121",
  },
  middleburycollege: {
    aliases: ["Middlebury", "Midd"],
    state: "VT",
    control: "private",
    color: "#0D395F",
  },
  barnardcollege: {
    aliases: ["Barnard", "Barnard University"],
    state: "NY",
    control: "private",
    color: "#002F6C",
  },
  colbycollege: {
    aliases: ["Colby"],
    state: "ME",
    control: "private",
    color: "#002169",
  },
  grinnellcollege: {
    aliases: ["Grinnell"],
    state: "IA",
    control: "private",
    color: "#DA291C",
  },
  wpi: {
    aliases: ["WPI", "Worcester Poly"],
    state: "MA",
    control: "private",
    color: "#AC2B37",
  },
  uconn: {
    aliases: ["UConn", "UConn Storrs", "University of Connecticut"],
    state: "CT",
    control: "public",
    color: "#000E2F",
  },
  universityofrichmond: {
    aliases: ["U of R", "URichmond", "University of Richmond", "Richmond", "Richmond Spiders"],
    state: "VA",
    control: "private",
    color: "#990000",
  },
  colgate: {
    aliases: ["Colgate"],
    state: "NY",
    control: "private",
    color: "#821019",
  },
  reedcollege: {
    aliases: ["Reed", "Reed College"],
    state: "OR",
    control: "private",
    color: "#A70E16",
  },
  // TODO: set official colors for these three (they currently use the default gray).
  pomonacollege: {
    aliases: ["Pomona", "Pomona College"],
    state: "CA",
    control: "private",
    color: "#4B5563",
  },
  swarthmorecollege: {
    aliases: ["Swarthmore", "Swat"],
    state: "PA",
    control: "private",
    color: "#4B5563",
  },
  bowdoincollege: { aliases: ["Bowdoin"], state: "ME", control: "private", color: "#4B5563" },
  bucknell: {
    aliases: ["Bucknell"],
    state: "PA",
    control: "private",
    color: "#003865",
  },
  lafayette: {
    aliases: ["Lafayette"],
    state: "PA",
    control: "private",
    color: "#910029",
  },
  macalester: {
    aliases: ["Macalester", "Mac"],
    state: "MN",
    control: "private",
    color: "#01426A",
  },
  batescollege: {
    aliases: ["Bates"],
    state: "ME",
    control: "private",
    color: "#881124",
  },
  brynmawr: {
    aliases: ["Bryn Mawr", "BMC"],
    state: "PA",
    control: "private",
    color: "#FFC600",
  },
  mountholyoke: {
    aliases: ["Mount Holyoke", "MHC", "Mt. Holyoke"],
    state: "MA",
    control: "private",
    color: "#004876",
  },
  occidental: {
    aliases: ["Occidental", "Oxy"],
    state: "CA",
    control: "private",
    color: "#FF671F",
  },
  haverfordcollege: {
    aliases: ["Haverford", "Fords"],
    state: "PA",
    control: "private",
    color: "#8B0000",
  },
  kenyoncollege: {
    aliases: ["Kenyon"],
    state: "OH",
    control: "private",
    color: "#4B2E84",
  },
  oberlincollege: {
    aliases: ["Oberlin", "Oberlin College"],
    state: "OH",
    control: "private",
    color: "#A6192E",
  },
  universityofdelaware: {
    aliases: ["UDel", "Delaware", "UD"],
    state: "DE",
    control: "public",
    color: "#00539F",
  },
};

export const schoolDataMap: Record<string, SchoolData> = Object.fromEntries(
  allSchools.map((school) => [school.slug, school]),
);

export const SCHOOL_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(SCHOOL_METADATA).map(([slug, metadata]) => [slug, metadata.color]),
);

export const SCHOOL_ALIASES: Record<string, string[]> = Object.fromEntries(
  Object.entries(SCHOOL_METADATA).map(([slug, metadata]) => [slug, metadata.aliases ?? []]),
);

export const FEATURED_SCHOOL_SLUGS = Object.entries(SCHOOL_METADATA)
  .filter(([, metadata]) => metadata.featured)
  .map(([slug]) => slug);

export const featuredSchools: SchoolData[] = FEATURED_SCHOOL_SLUGS.map(
  (slug) => schoolDataMap[slug],
).filter((school): school is SchoolData => Boolean(school));

export const availableSchoolSlugs = allSchools.map((school) => school.slug);

export const searchableSchools: SearchableSchool[] = allSchools.map((school) => {
  const latestYear = getLatestYear(school);
  const latestData = latestYear ? school.years[latestYear] : null;

  return {
    name: school.name,
    slug: school.slug,
    acceptanceRate: latestData?.admissions.acceptanceRate ?? 0,
    aliases: SCHOOL_ALIASES[school.slug] ?? [],
  };
});

export function getSchoolColor(slug: string): string {
  return SCHOOL_COLORS[slug] ?? "#4B5563";
}

/**
 * Small, serializable summary of a school for cards, chips and lists.
 * Client components receive these as props instead of importing the full
 * school JSON, which would ship every school's data to the browser.
 */
export interface SchoolCardData {
  slug: string;
  name: string;
  color: string;
  yearCount: number;
  yearRange: string;
  acceptanceRate: number | null;
  enrolled: number | null;
  yieldRate: number | null;
  satP25: number | null;
  satP50: number | null;
  satP75: number | null;
  totalCOA: number | null;
  state: string;
  control: SchoolControl;
}

function toSchoolCardData(school: SchoolData): SchoolCardData | null {
  const latestYear = getLatestYear(school);
  const latest = latestYear ? school.years[latestYear] : null;
  const yearRange = getSchoolYearRange(school);
  if (!latest || !yearRange) return null;
  const sat = latest.testScores.sat?.composite;

  return {
    slug: school.slug,
    name: school.name,
    color: getSchoolColor(school.slug),
    yearCount: getSortedYears(school).length,
    yearRange,
    acceptanceRate: latest.admissions.acceptanceRate ?? null,
    enrolled: latest.admissions.enrolled ?? null,
    yieldRate: latest.admissions.yield ?? null,
    satP25: sat?.p25 ?? null,
    satP50: sat?.p50 ?? null,
    satP75: sat?.p75 ?? null,
    totalCOA: latest.costs.totalCOA ?? null,
    state: SCHOOL_METADATA[school.slug]?.state ?? "",
    control: SCHOOL_METADATA[school.slug]?.control ?? "private",
  };
}

export const schoolCards: SchoolCardData[] = allSchools
  .map(toSchoolCardData)
  .filter((card): card is SchoolCardData => card !== null);

export const schoolCardMap: Record<string, SchoolCardData> = Object.fromEntries(
  schoolCards.map((card) => [card.slug, card]),
);
