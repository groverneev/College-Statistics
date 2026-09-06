import CSUPageClient from "./CSUPageClient";

export const metadata = {
  title: "CSU Campus Explorer – College Statistics",
  description:
    "Explore California State University admissions by campus, discipline and major. Compare admit rates, yield and freshman versus transfer entry across all 23 CSU campuses for Fall 2021–2025, alongside county-level a-g completion.",
};

export default function CSUPage() {
  return <CSUPageClient />;
}
