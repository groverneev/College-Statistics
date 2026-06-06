import Link from "next/link";
import { featuredSchools } from "@/data/schools";
import SchoolCard from "@/components/SchoolCard";

export default function HomePageContent() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">
          Featured Schools
        </h2>
        <Link
          href="/schools"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          Browse all schools &rarr;
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featuredSchools.map((school) => (
          <SchoolCard key={school.slug} school={school} showSaveButton />
        ))}
      </div>
    </div>
  );
}
