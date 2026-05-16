import { TrainingGroupsPanel } from "@/components/dashboard/training-groups-panel";

export default function GroupsPage() {
  return (
    <div className="page-wrap">
      <header className="page-titlebar visual-card">
        <p className="text-xs font-bold uppercase tracking-wide text-muted">Group templates</p>
        <h1 className="text-3xl font-bold text-ink">Groups</h1>
        <p className="mt-1 max-w-3xl text-sm text-muted">Manage recurring rosters and workout templates before they become live session attendance.</p>
      </header>
      <div className="grid min-h-[680px] max-w-xl">
        <TrainingGroupsPanel />
      </div>
    </div>
  );
}
