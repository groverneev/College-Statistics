import SearchBar from "@/components/SearchBar";
import SortableSchools from "@/components/SortableSchools";
import { allSchools, schoolCards, searchableSchools } from "@/data/schools";
import { pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "Browse Colleges: Acceptance Rates, SAT Scores & Costs – College Statistics",
  description: `Compare acceptance rates, SAT ranges, class sizes, yield and cost of attendance for ${allSchools.length} top U.S. colleges, sourced from official Common Data Set reports.`,
  path: "/schools",
});

export default function BrowseSchoolsPage() {
  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-12 px-4 text-center text-white">
        <h1 className="text-3xl md:text-4xl font-bold mb-3">Browse Schools</h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto mb-6">
          Explore Common Data Set metrics across top universities.
        </p>
        <SearchBar schools={searchableSchools} />
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12">
        <SortableSchools schools={schoolCards} />
      </div>
    </div>
  );
}
