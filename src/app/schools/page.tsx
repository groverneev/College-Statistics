import SearchBar from "@/components/SearchBar";
import SchoolCard from "@/components/SchoolCard";
import { allSchools, searchableSchools } from "@/data/schools";

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
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">
          All Schools ({allSchools.length})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allSchools.map((school) => (
            <SchoolCard key={school.slug} school={school} showSaveButton />
          ))}
        </div>
      </div>
    </div>
  );
}
