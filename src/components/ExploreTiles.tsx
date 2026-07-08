import Link from "next/link";

interface Tile {
  href: string;
  title: string;
  description: string;
  cta: string;
  visual: React.ReactNode;
}

const tiles: Tile[] = [
  {
    href: "/schools",
    title: "Browse & Compare",
    description:
      "Sort every school by acceptance rate, class size, test scores, cost, and yield.",
    cta: "Browse schools",
    visual: (
      // Sorted bars
      <svg viewBox="0 0 120 40" className="w-28 h-10" aria-hidden>
        <rect x="0" y="4" width="104" height="7" rx="3.5" fill="rgba(255,255,255,0.14)" />
        <rect x="0" y="16" width="72" height="7" rx="3.5" fill="#53A8E8" />
        <rect x="0" y="28" width="44" height="7" rx="3.5" fill="rgba(255,255,255,0.14)" />
      </svg>
    ),
  },
  {
    href: "/uc",
    title: "UC Campus Explorer",
    description:
      "Compare admit rates, GPA ranges, and yield across all nine UC campuses by discipline.",
    cta: "Explore UC data",
    visual: (
      // Nine campuses
      <svg viewBox="0 0 120 40" className="w-28 h-10" aria-hidden>
        {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <circle
            key={i}
            cx={10 + (i % 5) * 22}
            cy={i < 5 ? 10 : 30}
            r="5"
            fill={i % 2 === 0 ? "#53A8E8" : "#FFB81C"}
            opacity={0.55 + (i % 3) * 0.15}
          />
        ))}
      </svg>
    ),
  },
  {
    href: "/trends",
    title: "Trends & Stories",
    description:
      "Data-driven analysis of application volumes, selectivity, and shifts in who's applying.",
    cta: "Read the trends",
    visual: (
      // Sparkline
      <svg viewBox="0 0 120 40" className="w-28 h-10" aria-hidden>
        <path
          d="M2 32 C 18 30, 26 24, 38 22 S 62 26, 74 18 S 102 6, 118 4"
          fill="none"
          stroke="#AE66F0"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <circle cx="118" cy="4" r="3" fill="#AE66F0" />
      </svg>
    ),
  },
];

export default function ExploreTiles() {
  return (
    <div className="max-w-6xl mx-auto px-4 pt-16 pb-24">
      <h2 className="section-label mb-5">Explore</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tiles.map((tile) => (
          <Link key={tile.href} href={tile.href} className="group">
            <div className="explore-card rounded-xl p-6 h-full flex flex-col">
              <div className="mb-5">{tile.visual}</div>
              <h3
                className="text-lg font-semibold mb-1.5"
                style={{ color: "#f7f8f8" }}
              >
                {tile.title}
              </h3>
              <p className="text-sm flex-1" style={{ color: "#8a8f98" }}>
                {tile.description}
              </p>
              <span
                className="mt-5 text-sm font-medium"
                style={{ color: "#c9cdd3" }}
              >
                {tile.cta}{" "}
                <span
                  aria-hidden
                  className="inline-block transition-transform group-hover:translate-x-0.5"
                >
                  &rarr;
                </span>
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
