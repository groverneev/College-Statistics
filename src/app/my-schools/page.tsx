import { redirect } from "next/navigation";
import SavedSchoolsDashboard from "@/components/SavedSchoolsDashboard";
import { getSession } from "@/lib/savedSchools";

export const metadata = {
  title: "My Schools – College Statistics",
  robots: { index: false, follow: false },
};

export default async function MySchoolsPage() {
  const session = await getSession();
  // Signed out — send them home instead of showing a 404
  if (!session) {
    redirect("/");
  }

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      <SavedSchoolsDashboard />
    </div>
  );
}
