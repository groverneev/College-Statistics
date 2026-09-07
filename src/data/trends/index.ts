export interface TrendMeta {
  slug: string;
  title: string;
  subtitle: string;
  date: string; // ISO: "2026-03-01"
  tags: string[];
  preview: string;
}

export const trends: TrendMeta[] = [
  {
    slug: "international-enrollment-exposure",
    title: "International Students Make Up More Than 10% of Undergraduates at Half of Leading Colleges",
    subtitle:
      "30 of 58 schools reported double-digit international enrollment in 2024–25; long-term trends split in both directions",
    date: "2026-09-06",
    tags: ["International Students", "Enrollment", "Admissions", "Common Data Set"],
    preview:
      "30 of 58 schools in the 2024–25 comparison reported international undergraduates at 10% or more. Across 40 schools with endpoint data, 24 gained share and 13 declined.",
  },
  {
    slug: "cs-enrollment-reversal",
    title: "Computer Science Interest Turns Down Across Every Level, 2024–2026",
    subtitle:
      "AP exams, the UC system, elite privates, and national counts all reversed together",
    date: "2026-07-07",
    tags: ["Computer Science", "Enrollment", "AP Exams", "AI"],
    preview:
      "After two decades as the fastest-growing field in American education, CS interest turned down everywhere at once: AP CS A down 17% from its 2024 peak, UC majors down 9%, and national enrollment posting the steepest drop of any field — right as GenAI coding tools arrived.",
  },
  {
    slug: "common-app-2026",
    title: "2026 Application Season: Five Fault Lines",
    subtitle: "Record totals mask growing divides in who's applying, and where",
    date: "2026-03-07",
    tags: ["Common App", "Applications", "2026", "Admissions"],
    preview:
      "1.4 million applicants, 9.2 million applications — but the aggregate surge hides five sharp divergences: a first-gen boom, a 9% international cliff, the return of test scores, and why the most selective schools are the slowest-growing.",
  },
  {
    slug: "uc-2026-applications",
    title: "UC Applications in 2026: Santa Cruz Surges, System Stays Flat",
    subtitle: "Campus-level divergence hidden beneath a near-flat system total",
    date: "2026-03-01",
    tags: ["UC System", "Applications", "2026"],
    preview:
      "System-wide UC first-year applications barely moved (+0.1%), but Santa Cruz jumped 19% and Merced transfers spiked 73% — a story of uneven growth across campuses.",
  },
];
