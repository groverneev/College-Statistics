import Link from "next/link";
import SchoolCard from "@/components/SchoolCard";
import { allSchools } from "@/data/schools";

export default function SchoolCarousel() {
  return (
    <div className="pt-4 pb-8 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 flex items-baseline justify-between mb-5">
        <h2 className="section-label">All {allSchools.length} schools</h2>
        <Link href="/schools" className="text-sm font-medium link-dark whitespace-nowrap">
          Browse all &rarr;
        </Link>
      </div>

      <div className="marquee-mask">
        <div className="marquee-track">
          {/* Two identical copies make the -50% translate loop seamless. The
              second is decorative only, so it's hidden from AT and tab order. */}
          {[0, 1].map((copy) => (
            <div
              key={copy}
              className="flex"
              aria-hidden={copy === 1 || undefined}
              inert={copy === 1 || undefined}
            >
              {allSchools.map((school) => (
                <div
                  key={`${copy}-${school.slug}`}
                  className="w-80 flex-shrink-0 mr-4"
                >
                  <SchoolCard school={school} showSaveButton />
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
