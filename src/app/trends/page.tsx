import { trends } from "@/data/trends/index";
import StoryCard from "@/components/trends/StoryCard";

export const metadata = {
  title: "Trends – College Statistics",
  description:
    "Data-driven analysis of college admissions trends, application volumes, and more.",
};

export default function TrendsPage() {
  const sorted = [...trends].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 px-4 text-center text-white">
        <h1 className="text-4xl md:text-5xl font-bold mb-3">Trends</h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto">
          Data-driven stories on college admissions, application volumes, and
          higher education statistics.
        </p>
      </div>

      {/* Story Grid */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        {sorted.length === 0 ? (
          <p className="text-center text-gray-500">No stories yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sorted.map((story) => (
              <StoryCard key={story.slug} story={story} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
