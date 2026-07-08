export interface ApCsaYearRow {
  year: number;
  testTakers: number;
}

// AP Computer Science A test takers, 2002–2026 (2026 preliminary)
export const apCsaSeries: ApCsaYearRow[] = [
  { year: 2002, testTakers: 15660 },
  { year: 2003, testTakers: 14674 },
  { year: 2004, testTakers: 14337 },
  { year: 2005, testTakers: 13924 },
  { year: 2006, testTakers: 14662 },
  { year: 2007, testTakers: 15049 },
  { year: 2008, testTakers: 15537 },
  { year: 2009, testTakers: 16622 },
  { year: 2010, testTakers: 20120 },
  { year: 2011, testTakers: 22176 },
  { year: 2012, testTakers: 26103 },
  { year: 2013, testTakers: 31117 },
  { year: 2014, testTakers: 39278 },
  { year: 2015, testTakers: 48994 },
  { year: 2016, testTakers: 57937 },
  { year: 2017, testTakers: 60519 },
  { year: 2018, testTakers: 65133 },
  { year: 2019, testTakers: 69685 },
  { year: 2020, testTakers: 70580 },
  { year: 2021, testTakers: 63980 },
  { year: 2022, testTakers: 77753 },
  { year: 2023, testTakers: 94438 },
  { year: 2024, testTakers: 98136 },
  { year: 2025, testTakers: 93217 },
  { year: 2026, testTakers: 81500 },
];

export interface CsSplitRow {
  year: number;
  csa: number;
  csp: number;
}

// AP CS A vs AP CS Principles test takers, 2022–2026 (2026 preliminary)
export const csSplitSeries: CsSplitRow[] = [
  { year: 2022, csa: 77753, csp: 134651 },
  { year: 2023, csa: 94438, csp: 164505 },
  { year: 2024, csa: 98136, csp: 175261 },
  { year: 2025, csa: 93217, csp: 175174 },
  { year: 2026, csa: 81500, csp: 163000 },
];

export interface SciIndexedRow {
  year: number;
  biologyIdx: number;
  chemistryIdx: number;
  physics1Idx: number;
  csaIdx: number;
  biologyCount: number;
  chemistryCount: number;
  physics1Count: number;
  csaCount: number;
}

// AP science exams indexed to their own 2024 totals (2024 = 100)
export const sciIndexedSeries: SciIndexedRow[] = [
  {
    year: 2024,
    biologyIdx: 100,
    chemistryIdx: 100,
    physics1Idx: 100,
    csaIdx: 100,
    biologyCount: 260062,
    chemistryCount: 151121,
    physics1Count: 164481,
    csaCount: 98136,
  },
  {
    year: 2025,
    biologyIdx: 110,
    chemistryIdx: 112,
    physics1Idx: 106,
    csaIdx: 95,
    biologyCount: 287232,
    chemistryCount: 170000,
    physics1Count: 174000,
    csaCount: 93217,
  },
  {
    year: 2026,
    biologyIdx: 122,
    chemistryIdx: 122,
    physics1Idx: 112,
    csaIdx: 83,
    biologyCount: 318000,
    chemistryCount: 185000,
    physics1Count: 184000,
    csaCount: 81500,
  },
];

export interface DeclineSourceRow {
  source: string;
  window: string;
  change: number;
}

// CS enrollment declines by independent source (measurement windows differ)
export const declinesBySource: DeclineSourceRow[] = [
  { source: "AP CS A", window: "2024 → 2026", change: -17 },
  { source: "UC CS majors", window: "2023 → 2025", change: -9 },
  { source: "Nat'l CS + info sci", window: "NSC, Fall 2025", change: -8.1 },
  { source: "Nat'l CS only", window: "NSC, Fall 2025", change: -11.2 },
  { source: "CS + programming", window: "Goldman, 2025–26", change: -10 },
];

export const lede = `
For two decades, computer science was the fastest-growing corner of American
education. That trend has now reversed at the same moment across four independent
datasets: high school AP exams, the University of California system, elite private
universities, and national enrollment counts. Between 2002 and 2024, AP Computer
Science A grew more than sixfold, and undergraduate CS enrollment roughly doubled
over the last ten years alone. This piece lays out the numbers and the factors
analysts have attached to them, without asserting which of those factors is doing
the work.
`.trim();

export const sections = {
  apPeak: {
    heading: "High school: AP Computer Science A peaks, then falls two years running",
    body: `AP Computer Science A, the exam's programming-heavy track, grew almost every
year from 15,660 test takers in 2002 to a peak of 98,136 in 2024. It has fallen in
each of the two years since. The 2026 count is down about 17% from the 2024 peak,
erasing roughly three years of growth and returning the exam to its 2022–2023 range.
Enrollment in the other major lab sciences, by contrast, has kept climbing.`,
  },
  labSciences: {
    heading: "Meanwhile, the lab sciences kept climbing",
    body: `The decline is more striking because it runs against CS A's own field. Over
the same two years, AP Biology, Chemistry, and Physics 1 each grew by double digits.
Some of that is a rising tide, as overall AP participation grew about 7% from 2024 to
2025, but CS A fell while the other sciences rose, making it one of the few STEM exams
to shrink at all. By 2026, Biology and Chemistry are up about 22% and Physics 1 about
12%, while CS A is down about 17%.`,
  },
  csaVsCsp: {
    heading: "The AP CSA vs. CSP split",
    body: `The decline is sharper in the rigorous programming course than in the
conceptual one. AP Computer Science Principles, the broader survey course that does
not require Java, drew 175,261 test takers in 2024 and about 163,000 in 2026, a drop
of roughly 7%. Over the same window, AP CSA fell about 17%, roughly two and a half
times faster. Interest in serious coding is cooling faster than interest in general
computing literacy.`,
  },
  ucSystem: {
    heading: "University of California: first sustained decline since the dot-com bust",
    body: `UC-wide, 12,652 undergraduates are majoring in computer science in 2025,
down 6% from 2024 on top of a 3% drop the year before — a 9% decline over two years
and the first sustained retreat since the early-2000s dot-com bust. The total is back
to roughly its 2021 level, though still nearly double where it stood a decade ago.
One campus bucked the trend: UC San Diego, the only UC with a dedicated undergraduate
AI major, where about one in five applications to the CS department now target that
AI track.`,
  },
  elitePrivates: {
    heading: "Elite private universities: the same shape",
    bullets: [
      "Princeton: Computer science was the single most popular major from 2011 through 2017 and held that rank through the Class of 2025. Fewer students are now declaring it, while electrical and computer engineering rises.",
      "Stanford: CS enrollment has stalled after years of steady growth.",
      'MIT: The "Artificial Intelligence and Decision Making" major, launched in 2022, is now the second-largest major on campus at roughly 330 students, behind only CS.',
    ],
  },
  nationalContext: {
    heading: "National context",
    body: `Separate national counts confirm the pattern, and it is the steepest move in
computing enrollment in years. The National Student Clearinghouse reports computer and
information science enrollment fell 8.1% in fall 2025, the steepest drop of any field
of study, with computer science specifically down 11.2%. Goldman Sachs found CS and
programming enrollment each fell more than 10% in 2025–26, which it framed as the
first clear evidence students are steering away from majors exposed to AI. Individual
campuses show the same: Arizona State CS down about 14% between fall 2024 and fall
2025; Washington University in St. Louis down 16% over two years.`,
  },
  whereAndWhy: {
    heading: "Where the students are going, and why",
    body: `The retreat is concentrated in traditional CS. Adjacent fields — data
science, cybersecurity, computer engineering, and dedicated AI programs like UC San
Diego's and MIT's — are flat or growing, so much of this is movement within computing
rather than away from it. Sources covering the decline cite a recurring set of
conditions, listed here as co-occurring variables, not established causes:`,
    bullets: [
      "Tech-sector layoffs (more than 100,000 in 2025, following larger cuts in 2024).",
      "AI coding tools reshaping entry-level software work and the perceived demand for junior developers.",
      "A tougher early-career job market, with recent-graduate unemployment above the national rate for five straight years.",
      "Migration toward specialized AI, cybersecurity, data science, and computer engineering degrees.",
    ],
    coda: "Which of these is decisive, and in what mix, is not something the enrollment data alone can settle.",
  },
};

export const takeaways = [
  "AP CS A test takers fell ~17% from the 2024 peak (98,136 → ~81,500), erasing roughly three years of growth",
  "AP Biology and Chemistry grew ~22% and Physics 1 ~12% over the same two years — CS A fell while every other lab science rose",
  "The rigorous CS A track is shrinking ~2.5x faster than the conceptual CS Principles course",
  "UC CS majors are down 9% over two years — the first sustained decline since the dot-com bust",
  "National Student Clearinghouse: CS enrollment down 11.2% in fall 2025, the steepest drop of any field",
  "Adjacent fields (AI, data science, cybersecurity, computer engineering) are flat or growing — much of the shift is within computing, not away from it",
  "The turn lines up with the arrival of generative AI coding tools, but the data alone can't settle which factor is decisive",
];

export interface SourceLink {
  label: string;
  url: string;
}

export const sourceLinks: SourceLink[] = [
  {
    label: "College Board — AP Computer Science A score distributions",
    url: "https://apstudents.collegeboard.org/about-ap-scores/score-distributions/ap-computer-science-a",
  },
  {
    label: "College Board — AP Computer Science Principles score distributions",
    url: "https://apstudents.collegeboard.org/about-ap-scores/score-distributions/ap-computer-science-principles",
  },
  {
    label: "AP Program — Trevor Packer, 2026 AP CSA results",
    url: "https://x.com/AP_Trevor/status/2071651160281231385",
  },
  {
    label: "University of California — Freshman admission by discipline",
    url: "https://www.universityofcalifornia.edu/about-us/information-center/freshman-admission-discipline",
  },
  {
    label: "San Francisco Chronicle (via GovTech) — UC CS majors decline",
    url: "https://www.govtech.com/education/higher-ed/cs-majors-decline-at-uc-for-first-time-since-early-2000s",
  },
  {
    label: "Princeton Alumni Weekly — Computer science majors decline",
    url: "https://paw.princeton.edu/article/computer-science-majors-decline-consistent-nationwide-trends",
  },
  {
    label: "Built In — CS degrees losing popularity (NSC, MIT AI major)",
    url: "https://builtin.com/articles/computer-science-degree-decline-ai",
  },
  {
    label: "Goldman Sachs (via Yahoo Finance) — Students ditching computer science",
    url: "https://finance.yahoo.com/technology/ai/articles/students-ditching-computer-science-ai-121215794.html",
  },
  {
    label: "Computing Research Association — 2025 Taulbee Survey",
    url: "https://cra.org/crn/2026/06/cra-update-new-cra-taulbee-survey-findings-show-record-degree-production-alongside-a-cooling-enrollment-pipeline/",
  },
  {
    label: "Computing Research Association — CERP enrollment pulse survey",
    url: "https://cra.org/crn/2025/10/cra-update-navigating-the-changing-landscape-of-computing-education-together/",
  },
];

export const sourceNote =
  "Figures for 2026 AP exams are preliminary. UC year-over-year figures are as reported by the San Francisco Chronicle.";
