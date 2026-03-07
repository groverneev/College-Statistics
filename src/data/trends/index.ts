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
