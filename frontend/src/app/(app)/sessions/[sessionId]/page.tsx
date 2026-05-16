import { CockpitGrid } from "@/components/cockpit/cockpit-grid";

export default async function SessionPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = await params;
  return <CockpitGrid sessionId={Number(sessionId)} />;
}
