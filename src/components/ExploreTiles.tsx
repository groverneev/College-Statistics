import Link from "next/link";

interface Tile {
  href: string;
  title: string;
  description: string;
  cta: string;
  icon: React.ReactNode;
}

const tiles: Tile[] = [
  {
    href: "/schools",
    title: "Browse & Compare",
    description:
      "Sort every school by acceptance rate, class size, test scores, cost, and yield.",
    cta: "Browse schools",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 6h18M3 12h18M3 18h18" />
      </svg>
    ),
  },
  {
    href: "/uc",
    title: "UC Campus Explorer",
    description:
      "Compare admit rates, GPA ranges, and yield across all nine UC campuses by discipline.",
    cta: "Explore UC data",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
  },
  {
    href: "/trends",
    title: "Trends & Stories",
    description:
      "Data-driven analysis of application volumes, selectivity, and shifts in who's applying.",
    cta: "Read the trends",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 17l6-6 4 4 8-8m0 0h-5m5 0v5" />
      </svg>
    ),
  },
];

export default function ExploreTiles() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">
        Three ways to explore
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {tiles.map((tile) => (
          <Link key={tile.href} href={tile.href}>
            <div className="card p-6 h-full flex flex-col hover:shadow-lg transition-shadow cursor-pointer">
              <div className="w-11 h-11 rounded-lg bg-gray-100 flex items-center justify-center text-gray-700 mb-4">
                {tile.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">
                {tile.title}
              </h3>
              <p className="text-sm text-gray-600 flex-1">{tile.description}</p>
              <span className="mt-4 text-sm font-medium text-blue-600">
                {tile.cta}{" "}&rarr;
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
