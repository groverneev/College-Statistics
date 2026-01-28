import Link from "next/link";
import { SchoolData } from "@/lib/types";

// Import school data
import brownData from "@/data/schools/brown.json";
import caltechData from "@/data/schools/caltech.json";
import cornellData from "@/data/schools/cornell.json";
import dartmouthData from "@/data/schools/dartmouth.json";
import harvardData from "@/data/schools/harvard.json";
import princetonData from "@/data/schools/princeton.json";
import stanfordData from "@/data/schools/stanford.json";
import uclaData from "@/data/schools/ucla.json";
import upennData from "@/data/schools/upenn.json";
import yaleData from "@/data/schools/yale.json";

const schools: SchoolData[] = [
  brownData as SchoolData,
  caltechData as SchoolData,
  cornellData as SchoolData,
  dartmouthData as SchoolData,
  harvardData as SchoolData,
  princetonData as SchoolData,
  stanfordData as SchoolData,
  uclaData as SchoolData,
  upennData as SchoolData,
  yaleData as SchoolData,
];

export default function HowItWorksPage() {
  const schoolCount = schools.length;
  const schoolNames = schools.map((s) => s.name).join(", ").replace(/, ([^,]*)$/, ", and $1");

  // Calculate the overall year range across all schools
  const allYears = new Set<string>();
  schools.forEach((school) => {
    Object.keys(school.years).forEach((year) => allYears.add(year));
  });
  const sortedYears = Array.from(allYears).sort();
  const yearRange = `${sortedYears[0]} through ${sortedYears[sortedYears.length - 1]}`;

  // Calculate min/max years per school for display
  const yearCounts = schools.map((s) => Object.keys(s.years).length);
  const minYears = Math.min(...yearCounts);
  const maxYears = Math.max(...yearCounts);
  const yearCountDisplay = minYears === maxYears ? `${maxYears}` : `${minYears}-${maxYears}`;
  const metrics = [
    {
      title: "Admissions",
      description:
        "Applications received, acceptance rates, yield rates, and early decision/action statistics",
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      title: "Test Scores",
      description:
        "SAT and ACT score distributions, including 25th, 50th, and 75th percentile ranges",
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
    },
    {
      title: "Costs",
      description:
        "Tuition, fees, room and board, and total cost of attendance breakdowns",
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      title: "Financial Aid",
      description:
        "Percentage receiving aid, average aid packages, need-based grants, and net price",
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      ),
    },
    {
      title: "Demographics",
      description:
        "Enrollment totals, racial/ethnic breakdowns, and geographic distribution",
      icon: (
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      ),
    },
  ];

  const steps = [
    {
      number: "1",
      title: "Select a School",
      description:
        "Browse our collection of universities on the home page and click on any school to view its detailed dashboard.",
    },
    {
      number: "2",
      title: "Explore the Data",
      description:
        "View interactive charts showing historical trends across admissions, test scores, costs, financial aid, and demographics.",
    },
    {
      number: "3",
      title: "Analyze Trends",
      description:
        "Compare data across multiple years to understand how metrics have changed over time at each institution.",
    },
    {
      number: "4",
      title: "Make Informed Decisions",
      description:
        "Use the data to inform your college search and application strategy with accurate, up-to-date information.",
    },
  ];

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 py-16 px-4 text-center text-white">
        <h1 className="text-4xl md:text-5xl font-bold mb-3">How it Works</h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto">
          Understanding the Common Data Set and how to use our dashboard
        </p>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* What is CDS */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            What is the Common Data Set?
          </h2>
          <p className="text-gray-600 mb-4">
            The Common Data Set (CDS) initiative is a collaborative effort among
            higher education institutions, The College Board, Peterson&apos;s, and
            U.S. News &amp; World Report. It establishes standardized data items
            and definitions to ensure consistent, comparable data about colleges
            and universities.
          </p>
          <p className="text-gray-600 mb-4">
            Each year, participating colleges complete the CDS survey, providing
            detailed information about their admissions process, enrolled
            students, academic offerings, student life, and financial aid. This
            data is used by:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
            <li>College ranking publications</li>
            <li>Guidebook publishers</li>
            <li>Students and families researching colleges</li>
            <li>High school counselors</li>
            <li>Educational researchers</li>
          </ul>
        </section>

        {/* Available Metrics */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Available Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {metrics.map((metric) => (
              <div
                key={metric.title}
                className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex-shrink-0 w-12 h-12 bg-gray-800 text-white rounded-lg flex items-center justify-center">
                  {metric.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">
                    {metric.title}
                  </h3>
                  <p className="text-sm text-gray-600">{metric.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How to Use */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            How to Use the Dashboard
          </h2>
          <div className="space-y-6">
            {steps.map((step) => (
              <div key={step.number} className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-10 h-10 bg-gray-800 text-white rounded-full flex items-center justify-center font-bold">
                  {step.number}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">
                    {step.title}
                  </h3>
                  <p className="text-gray-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Data Sources */}
        <section className="card p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Data Sources &amp; Accuracy
          </h2>
          <p className="text-gray-600 mb-4">
            All data on College Statistics is extracted directly from official
            Common Data Set reports published by each institution. We do not
            modify, interpolate, or estimate any values. If data is unavailable
            for a particular year or metric, it will be clearly indicated.
          </p>
          <p className="text-gray-600 mb-4">
            Our current coverage includes:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4 mb-4">
            <li>
              <strong>{schoolCount} universities</strong>: {schoolNames}
            </li>
            <li>
              <strong>{yearCountDisplay} years of data</strong> per school: Academic years {yearRange}
            </li>
            <li>
              <strong>50+ data points</strong> per school per year
            </li>
          </ul>
          <p className="text-gray-600">
            We continuously work to add more schools and verify data accuracy.
            If you notice any discrepancies, please{" "}
            <Link href="/contact" className="text-gray-800 underline">
              contact us
            </Link>
            .
          </p>
        </section>

        {/* CTA */}
        <div className="text-center mt-8">
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-gray-800 hover:bg-gray-900 text-white rounded-lg font-medium transition-colors"
          >
            Explore Schools
            <svg
              className="w-4 h-4 ml-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
