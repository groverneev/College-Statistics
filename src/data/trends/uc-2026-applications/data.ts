export interface CampusApplicationRow {
  campus: string;
  firstYear2025: number;
  firstYear2026: number;
  transfer2025: number;
  transfer2026: number;
}

export const campusData: CampusApplicationRow[] = [
  {
    campus: "Berkeley",
    firstYear2025: 126796,
    firstYear2026: 133128,
    transfer2025: 23313,
    transfer2026: 26216,
  },
  {
    campus: "Davis",
    firstYear2025: 102958,
    firstYear2026: 104850,
    transfer2025: 17173,
    transfer2026: 17421,
  },
  {
    campus: "Irvine",
    firstYear2025: 124214,
    firstYear2026: 125987,
    transfer2025: 25436,
    transfer2026: 27038,
  },
  {
    campus: "LA",
    firstYear2025: 145058,
    firstYear2026: 146672,
    transfer2025: 28239,
    transfer2026: 30645,
  },
  {
    campus: "Merced",
    firstYear2025: 48049,
    firstYear2026: 48499,
    transfer2025: 3696,
    transfer2026: 6401,
  },
  {
    campus: "Riverside",
    firstYear2025: 70578,
    firstYear2026: 72295,
    transfer2025: 12326,
    transfer2026: 14753,
  },
  {
    campus: "San Diego",
    firstYear2025: 136728,
    firstYear2026: 141752,
    transfer2025: 23422,
    transfer2026: 26314,
  },
  {
    campus: "Santa Barbara",
    firstYear2025: 110165,
    firstYear2026: 108503,
    transfer2025: 18818,
    transfer2026: 18866,
  },
  {
    campus: "Santa Cruz",
    firstYear2025: 66178,
    firstYear2026: 78832,
    transfer2025: 11595,
    transfer2026: 13501,
  },
];

export interface AppTypeMixRow {
  year: string;
  caResident: number;
  domesticOOS: number;
  international: number;
}

// System-wide first-year application type breakdown
export const appTypeMix: AppTypeMixRow[] = [
  {
    year: "Fall 2025",
    caResident: 130707,
    domesticOOS: 42336,
    international: 32115,
  },
  {
    year: "Fall 2026",
    caResident: 130211,
    domesticOOS: 43150,
    international: 32070,
  },
];

export const lede = `
UC-wide, the headline number barely moved: first-year applications held near flat
from Fall 2025 to Fall 2026. But that system total masks a striking divergence across
campuses. Santa Cruz saw a 19% surge in first-year applicants, while Merced's transfer
pool nearly doubled. Meanwhile, Berkeley continued its upward trajectory and Santa Barbara
was the only campus to decline. The story isn't how many students applied to the UC system
— it's where they're applying.
`.trim();

export const takeaways = [
  "System-wide first-year applications essentially flat: 205,158 → 205,431 (+0.1%)",
  "Santa Cruz first-year applications up 19.1% (66,178 → 78,832) — the largest campus jump",
  "Merced transfers nearly doubled: 3,696 → 6,401 (+73.3%)",
  "Berkeley first-year up 5.0% (126,796 → 133,128)",
  "Santa Barbara was the only campus with a first-year decline (-1.5%)",
  "International first-year applications flat system-wide: 32,115 → 32,070 (-0.1%)",
  "Domestic out-of-state first-year applications up modestly: 42,336 → 43,150 (+1.9%)",
];
