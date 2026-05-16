import { SessionSummaryView } from "@/components/sessions/session-summary-view";

export default async function SessionSummaryPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = await params;
  return <SessionSummaryView sessionId={Number(sessionId)} />;
}
