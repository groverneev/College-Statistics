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
    slug: "uc-2026-applications",
    title: "UC Applications in 2026: Santa Cruz Surges, System Stays Flat",
    subtitle: "Campus-level divergence hidden beneath a near-flat system total",
    date: "2026-03-01",
    tags: ["UC System", "Applications", "2026"],
    preview:
      "System-wide UC first-year applications barely moved (+0.1%), but Santa Cruz jumped 19% and Merced transfers spiked 73% — a story of uneven growth across campuses.",
  },
];
