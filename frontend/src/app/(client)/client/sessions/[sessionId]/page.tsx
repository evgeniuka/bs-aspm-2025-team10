import { ClientSessionSummaryView } from "@/components/clients/client-session-summary-view";

export default async function ClientSessionSummaryPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = await params;
  return <ClientSessionSummaryView sessionId={Number(sessionId)} />;
}
