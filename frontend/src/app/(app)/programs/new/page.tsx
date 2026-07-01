import { ProgramBuilder } from "@/components/programs/program-builder";

export default function NewProgramPage() {
  return (
    <div className="page-wrap max-w-[820px]">
      <header>
        <h1 className="text-2xl font-semibold text-ink">Build a program</h1>
        <p className="mt-1 text-sm text-muted">Pick a client and a focus, then fine-tune the plan.</p>
      </header>
      <ProgramBuilder />
    </div>
  );
}
