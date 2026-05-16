import { ClientProfileView } from "@/components/clients/client-profile-view";

export default async function ClientProfilePage({ params }: { params: Promise<{ clientId: string }> }) {
  const { clientId } = await params;
  return <ClientProfileView clientId={Number(clientId)} />;
}
