import { ImageResponse } from "next/og";
import { getSchoolColor, schoolDataMap } from "@/data/schools";
import { SITE_NAME } from "@/lib/seo";
import { formatNumber, formatPercent, getLatestYear } from "@/utils/dataHelpers";

export const alt = "College admissions statistics";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export function generateStaticParams() {
  return Object.keys(schoolDataMap).map((school) => ({ school }));
}

export default async function Image({ params }: { params: Promise<{ school: string }> }) {
  const { school } = await params;
  const schoolData = schoolDataMap[school.toLowerCase()];
  const color = schoolData ? getSchoolColor(schoolData.slug) : "#4B5563";
  const latestYear = schoolData ? getLatestYear(schoolData) : null;
  const latest = latestYear ? schoolData.years[latestYear] : null;
  const sat = latest?.testScores.sat?.composite;

  const stats = [
    { label: "Acceptance rate", value: formatPercent(latest?.admissions.acceptanceRate) },
    { label: "Applications", value: formatNumber(latest?.admissions.applied) },
    {
      label: "SAT middle 50%",
      value:
        typeof sat?.p25 === "number" && typeof sat?.p75 === "number"
          ? `${sat.p25}–${sat.p75}`
          : "—",
    },
  ];

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px",
          background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
          color: "white",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 32, opacity: 0.8, marginBottom: 16 }}>
            {`Admissions Statistics${latestYear ? ` · ${latestYear}` : ""}`}
          </div>
          <div style={{ fontSize: 72, fontWeight: 700, lineHeight: 1.1 }}>
            {schoolData?.name ?? SITE_NAME}
          </div>
        </div>
        <div style={{ display: "flex", gap: 32 }}>
          {stats.map((stat) => (
            <div
              key={stat.label}
              style={{
                display: "flex",
                flexDirection: "column",
                flex: 1,
                padding: "28px 32px",
                borderRadius: 20,
                background: "rgba(255, 255, 255, 0.14)",
              }}
            >
              <div style={{ fontSize: 26, opacity: 0.8, marginBottom: 8 }}>{stat.label}</div>
              <div style={{ fontSize: 50, fontWeight: 700, whiteSpace: "nowrap" }}>{stat.value}</div>
            </div>
          ))}
        </div>
        <div style={{ fontSize: 28, opacity: 0.8 }}>{`${SITE_NAME} · Common Data Set`}</div>
      </div>
    ),
    size
  );
}
