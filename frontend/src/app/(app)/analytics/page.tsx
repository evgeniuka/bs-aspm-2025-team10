import { TrainerAnalyticsPanel } from "@/components/dashboard/trainer-analytics-panel";

export default function AnalyticsPage() {
  return (
    <div className="page-wrap">
      <header className="page-titlebar visual-card">
        <p className="text-xs font-bold uppercase tracking-wide text-muted">Performance workspace</p>
        <h1 className="mt-1 text-3xl font-bold text-ink">Analytics</h1>
        <p className="mt-1 max-w-3xl text-sm text-muted">
          Workload, readiness, focus distribution, and client attention signals from real session logs.
        </p>
      </header>
      <TrainerAnalyticsPanel />
    </div>
  );
}
