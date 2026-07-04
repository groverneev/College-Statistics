import SearchBar from "@/components/SearchBar";
import HomePageContent from "@/components/HomePageContent";
import HomeSavedSchools from "@/components/HomeSavedSchools";
import ExploreTiles from "@/components/ExploreTiles";
import HomeDataTeaser from "@/components/HomeDataTeaser";
import { allSchools, searchableSchools } from "@/data/schools";
import { getSortedYears } from "@/utils/dataHelpers";

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

  const chips = [
    `${stats.schools} schools`,
    `${stats.schoolYears}+ school-years`,
    stats.yearSpan,
    "Official Common Data Sets",
  ].filter(Boolean) as string[];

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 px-4 text-center text-white">
        <h1 className="text-4xl md:text-5xl font-bold mb-3">
          College Statistics
        </h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto mb-8">
          Explore and compare Common Data Set metrics across top universities.
          View historical trends in admissions, test scores, costs, and more.
        </p>
        <SearchBar schools={searchableSchools} />

        <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-2 mt-8 text-sm text-gray-300">
          {chips.map((chip, index) => (
            <span key={chip} className="flex items-center gap-3">
              {index > 0 && (
                <span className="text-gray-500" aria-hidden>
                  &middot;
                </span>
              )}
              <span>{chip}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Personalized: only renders for logged-in users with saved schools */}
      <HomeSavedSchools />

      {/* Capability gateways */}
      <ExploreTiles />

      {/* Live proof of the trend data */}
      <HomeDataTeaser />

      {/* Sample of the full school catalog */}
      <HomePageContent />
    </div>
  );
}
