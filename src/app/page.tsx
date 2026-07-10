import Link from "next/link";
import SearchBar from "@/components/SearchBar";
import ExploreTiles from "@/components/ExploreTiles";
import SchoolCarousel from "@/components/SchoolCarousel";
import HomeSavedSchools from "@/components/HomeSavedSchools";
import HeroTrendChart, { HeroSeries, HeroPoint } from "@/components/HeroTrendChart";
import { allSchools, searchableSchools, schoolDataMap } from "@/data/schools";
import { getSortedYears } from "@/utils/dataHelpers";

// Registry brand colors tuned for legibility on the light hero chart
// (Harvard, MIT, and Northeastern are near-identical crimsons at full depth, so
// MIT takes a neutral charcoal and Northeastern a warmer orange-red to separate).
const HERO_SCHOOLS: { slug: string; label: string; color: string }[] = [
  { slug: "harvard", label: "Harvard", color: "#C0392B" },
  { slug: "mit", label: "MIT", color: "#6E7079" },
  { slug: "ucla", label: "UCLA", color: "#2D7DD2" },
  { slug: "nyu", label: "NYU", color: "#7B3FE4" },
  { slug: "northeastern", label: "Northeastern", color: "#E05A2B" },
];

function getHeroSeries(): HeroSeries[] {
  return HERO_SCHOOLS.flatMap(({ slug, label, color }) => {
    const school = schoolDataMap[slug];
    if (!school) return [];

    const points = getSortedYears(school)
      .map((year) => {
        const rate = school.years[year]?.admissions.acceptanceRate;
        const start = parseInt(year.split("-")[0], 10);
        return rate && !Number.isNaN(start) ? { year: start, rate } : null;
      })
      .filter((p): p is HeroPoint => p !== null);

    return points.length >= 2 ? [{ slug, name: label, color, points }] : [];
  });
}

function getHeroStats() {
  let schoolYears = 0;
  let minYear = Infinity;
  let maxYear = -Infinity;

  for (const school of allSchools) {
    const years = getSortedYears(school);
    schoolYears += years.length;
    for (const year of years) {
      const start = parseInt(year.split("-")[0], 10);
      const end = parseInt(year.split("-")[1] ?? year.split("-")[0], 10);
      if (!Number.isNaN(start)) minYear = Math.min(minYear, start);
      if (!Number.isNaN(end)) maxYear = Math.max(maxYear, end);
    }
  }

  const roundedYears = Math.floor(schoolYears / 10) * 10;

  return {
    schools: allSchools.length,
    schoolYears: roundedYears,
    yearSpan:
      Number.isFinite(minYear) && Number.isFinite(maxYear)
        ? `${minYear}–${maxYear}`
        : null,
  };
}

export default function HomePage() {
  const stats = getHeroStats();
  const heroSeries = getHeroSeries();

  const chips = [
    `${stats.schools} schools`,
    `${stats.schoolYears}+ school-years`,
    stats.yearSpan,
    "Official Common Data Sets",
  ].filter(Boolean) as string[];

  return (
    // -mt-16 pulls the dark canvas up behind the fixed translucent header
    <div className="min-h-screen -mt-16 hero-dark">
      {/* Hero Section */}
      <div className="relative overflow-hidden pt-32 pb-20 sm:pt-36 sm:pb-24 text-center">
        {/* Ambient glow at the top of the canvas */}
        <div
          aria-hidden
          className="absolute inset-x-0 top-0 h-80 pointer-events-none"
          style={{
            background:
              "radial-gradient(60% 100% at 50% 0%, rgba(94, 106, 210, 0.10) 0%, transparent 70%)",
          }}
        />

        <div className="relative max-w-6xl mx-auto px-6 sm:px-4">
          <div className="max-w-4xl mx-auto">
            <h1
              className="hero-rise text-4xl sm:text-5xl md:text-6xl font-semibold mb-5"
              style={{ color: "#0d0e10", letterSpacing: "-0.025em", lineHeight: 1.08 }}
            >
              Getting in keeps
              <br />
              getting harder.
            </h1>
            <p
              className="hero-rise text-base sm:text-lg max-w-2xl mx-auto mb-8"
              style={{ color: "#5a5f66", animationDelay: "0.1s" }}
            >
              Track a decade of admissions, test scores, financial aid, and more across top universities
            </p>
          </div>

          <div className="hero-rise relative z-20" style={{ animationDelay: "0.18s" }}>
            <SearchBar schools={searchableSchools} />
          </div>

          <div className="hero-rise mt-5" style={{ animationDelay: "0.21s" }}>
            <Link href="/schools" className="hero-browse-btn">
              Browse all Schools
              <span aria-hidden>&rarr;</span>
            </Link>
          </div>

          <div
            className="hero-rise flex flex-wrap items-center justify-center gap-x-3 gap-y-2 mt-7 mb-14 text-sm"
            style={{ color: "#6b7078", animationDelay: "0.24s" }}
          >
            {chips.map((chip, index) => (
              <span key={chip} className="flex items-center gap-3">
                {index > 0 && (
                  <span style={{ color: "#c4c8ce" }} aria-hidden>
                    &middot;
                  </span>
                )}
                <span>{chip}</span>
              </span>
            ))}
          </div>

          <HeroTrendChart series={heroSeries} />
        </div>
      </div>

      {/* Signed-in users see their saved list before the full catalog */}
      <HomeSavedSchools />

      {/* Full catalog as an auto-scrolling marquee of school cards */}
      <SchoolCarousel />

      {/* Capability gateways */}
      <ExploreTiles />
    </div>
  );
}
