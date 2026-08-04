import SearchBar from "@/components/SearchBar";
import SchoolCard from "@/components/SchoolCard";
import SortableSchools, {
  type SortableSchoolItem,
} from "@/components/SortableSchools";
import { allSchools, searchableSchools } from "@/data/schools";
import { getLatestYearData, getSortedYears } from "@/utils/dataHelpers";

export default function BrowseSchoolsPage() {
  // Build the lightweight sort payload + pre-rendered cards on the server so the
  // client component only reorders (it never receives the full dataset).
  const items: SortableSchoolItem[] = allSchools.map((school) => {
    const latest = getLatestYearData(school);
    const sat = latest?.testScores.sat?.composite;

    return {
      slug: school.slug,
      metric: {
        slug: school.slug,
        name: school.name,
        acceptanceRate: latest?.admissions.acceptanceRate ?? null,
        classSize: latest?.admissions.enrolled ?? null,
        satMid: sat?.p50 ?? null,
        totalCost: latest?.costs.totalCOA ?? null,
        yieldRate: latest?.admissions.yield ?? null,
        yearsOfData: getSortedYears(school).length,
      },
      card: <SchoolCard school={school} showSaveButton />,
    };
  });

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
        <SortableSchools items={items} />
      </div>
    </div>
  );
}
