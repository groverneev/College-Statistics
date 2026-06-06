import { notFound } from "next/navigation";
import SavedSchoolsDashboard from "@/components/SavedSchoolsDashboard";
import { getSession } from "@/lib/savedSchools";

export default async function MySchoolsPage() {
  const session = await getSession();
  // Signed out — this page doesn't exist for you
  if (!session) {
    notFound();
  }

  return (
    <div className="min-h-screen" style={{ background: "#f5f5f5" }}>
      <SavedSchoolsDashboard />
    </div>
  );
}
