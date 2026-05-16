import { ProgramEditor } from "@/components/programs/program-editor";

export default async function ProgramPage({ params }: { params: Promise<{ programId: string }> }) {
  const { programId } = await params;
  return <ProgramEditor programId={Number(programId)} />;
}
