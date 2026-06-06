import SearchBar from "@/components/SearchBar";
import HomePageContent from "@/components/HomePageContent";
import { searchableSchools } from "@/data/schools";

export default function HomePage() {
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
      </div>

      {/* Featured schools — same view for all visitors */}
      <HomePageContent />
    </div>
  );
}
