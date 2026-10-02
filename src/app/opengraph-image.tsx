import { ImageResponse } from "next/og";
import { allSchools } from "@/data/schools";
import { SITE_NAME } from "@/lib/seo";

export const alt = "College Statistics – college admissions data from the Common Data Set";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
          background: "linear-gradient(135deg, #1f2937 0%, #111827 100%)",
          color: "white",
        }}
      >
        <div style={{ fontSize: 36, color: "#9ca3af", marginBottom: 24 }}>{SITE_NAME}</div>
        <div style={{ fontSize: 76, fontWeight: 700, lineHeight: 1.1, marginBottom: 32 }}>
          College Admissions Data, Simplified
        </div>
        <div style={{ fontSize: 34, color: "#d1d5db" }}>
          {`Acceptance rates, SAT scores, costs and aid for ${allSchools.length} colleges, from official Common Data Set reports`}
        </div>
      </div>
    ),
    size
  );
}
