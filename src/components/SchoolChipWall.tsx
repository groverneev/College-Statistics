import Link from "next/link";
import { allSchools, getSchoolColor } from "@/data/schools";

export default function SchoolChipWall() {
  return (
    <div className="max-w-5xl mx-auto px-4 pt-24 pb-28 text-center">
      <h2
        className="text-3xl sm:text-4xl font-semibold text-white mb-4"
        style={{ letterSpacing: "-0.02em" }}
      >
        Every number, from the source.
      </h2>
      <p
        className="text-base sm:text-lg max-w-xl mx-auto mb-8"
        style={{ color: "#8a8f98" }}
      >
        {allSchools.length} universities, each backed by its official Common
        Data Set filings — no estimates, no scraped rankings.
      </p>

      <div className="flex flex-wrap items-center justify-center gap-3 mb-14">
        <Link
          href="/schools"
          className="btn-primary-light rounded-full px-6 py-3 text-sm font-semibold"
        >
          {`Browse all ${allSchools.length} schools →`}
        </Link>
        <Link
          href="/uc"
          className="btn-ghost-dark rounded-full px-6 py-3 text-sm font-medium"
        >
          UC Explorer
        </Link>
      </div>

      <div className="flex flex-wrap justify-center gap-2">
        {allSchools.map((school) => (
          <Link
            key={school.slug}
            href={`/${school.slug}`}
            className="chip-dark flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium"
          >
            <span
              className="w-1.5 h-1.5 rounded-full flex-shrink-0"
              style={{
                background: `color-mix(in srgb, ${getSchoolColor(school.slug)} 60%, white)`,
              }}
              aria-hidden
            />
            {school.name}
          </Link>
        ))}
      </div>
    </div>
  );
}
