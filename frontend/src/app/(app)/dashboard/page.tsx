"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertCircle, CalendarDays, CheckCircle2, Dumbbell, RotateCw, Users } from "lucide-react";
import type { ReactNode } from "react";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import { StartSessionPanel } from "@/components/dashboard/start-session-panel";
import { TrainingGroupsPanel } from "@/components/dashboard/training-groups-panel";
import { ProgramBuilder } from "@/components/programs/program-builder";
import { Card, CardBody } from "@/components/ui/card";

type DashboardData = NonNullable<Awaited<ReturnType<typeof api.dashboard>>>;

export default function DashboardPage() {
  const [groupPresetId, setGroupPresetId] = useState<number | null>(null);
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.dashboard,
    retry: false
  });
  const prepareGroup = useCallback((groupId: number) => setGroupPresetId(groupId), []);
  const clearPreparedGroup = useCallback(() => setGroupPresetId(null), []);

  if (isLoading) {
    return <DashboardLoading />;
  }

  if (error || !data) {
    return <DashboardError error={error} isRetrying={isRefetching} onRetry={() => refetch()} />;
  }

  return (
    <div className="h-screen overflow-hidden p-3" id="dashboard" tabIndex={-1}>
      <div className="grid h-full min-h-0 gap-3 xl:grid-cols-[310px_minmax(0,1fr)]">
        <aside className="hidden min-h-0 flex-col gap-3 overflow-hidden xl:flex" id="program-builder">
          <SessionTunnelCard activeSessionId={data.active_session?.id ?? null} />
          <TrainingGroupsPanel onPrepareGroup={prepareGroup} variant="rail" />
          <ProgramBuilder variant="rail" />
        </aside>

        <main className="grid min-h-0 grid-rows-[auto_minmax(0,1fr)] gap-3">
          <DashboardHeader data={data} />
          <section className="min-h-0" id="live-session">
            <StartSessionPanel
              activeSession={data.active_session}
              groupPresetId={groupPresetId}
              readiness={data.today_readiness}
              onGroupPresetHandled={clearPreparedGroup}
            />
          </section>
        </main>
      </div>
    </div>
  );
}

function DashboardHeader({ data }: { data: DashboardData }) {
  return (
    <header className="visual-card px-4 py-3" id="analytics" tabIndex={-1}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="status-pill">
              <CalendarDays size={13} />
              Today
            </span>
            {data.active_session ? (
              <span className="status-pill border-emerald-200 bg-emerald-50 text-success">Live session active</span>
            ) : (
              <span className="status-pill">No active session</span>
            )}
          </div>
          <h1 className="mt-1 text-xl font-bold tracking-tight text-ink">Trainer dashboard</h1>
          <p className="mt-0.5 hidden max-w-2xl text-sm leading-5 text-muted min-[900px]:block">Everything needed to start coaching stays in this workspace.</p>
        </div>
        <div className="hidden grid-cols-3 gap-2 min-[900px]:grid">
          <MiniKpi label="Clients" value={data.total_clients} />
          <MiniKpi label="Programs" value={data.total_programs} />
          <MiniKpi label="Done" value={data.completed_sessions} />
        </div>
      </div>
    </header>
  );
}

function SessionTunnelCard({ activeSessionId }: { activeSessionId: number | null }) {
  return (
    <Card className="shrink-0 overflow-hidden p-2">
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <h2 className="truncate text-sm font-bold text-ink">Session tunnel</h2>
          <p className="text-xs text-muted">Roster to workout to cockpit</p>
        </div>
        {activeSessionId ? (
          <a
            className="inline-flex min-h-8 shrink-0 items-center justify-center gap-1.5 rounded-md bg-brand px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-700"
            href={routes.session(activeSessionId)}
          >
            <Activity size={13} />
            Resume
          </a>
        ) : (
          <a
            className="inline-flex min-h-8 shrink-0 items-center justify-center rounded-md border border-line bg-white px-3 py-1.5 text-xs font-semibold text-ink transition hover:bg-panel"
            href="#live-session"
          >
            Setup
          </a>
        )}
      </div>
      <div className="mt-2 grid grid-cols-3 gap-1.5">
        <TunnelStep icon={<Users size={13} />} label="Pick" state="Roster" />
        <TunnelStep icon={<Dumbbell size={13} />} label="Plan" state="Workout" />
        <TunnelStep icon={<CheckCircle2 size={13} />} label="Coach" state="1-10" />
      </div>
    </Card>
  );
}

function TunnelStep({ icon, label, state }: { icon: ReactNode; label: string; state: string }) {
  return (
    <div className="rounded-md border border-line bg-white/80 px-2 py-1.5 shadow-[0_1px_2px_rgba(16,24,40,0.04)]">
      <span className="flex items-center gap-1.5 text-[11px] font-bold text-ink">
        <span className="flex h-5 w-5 items-center justify-center rounded bg-panel text-brand">{icon}</span>
        <span className="truncate">{label}</span>
      </span>
      <span className="mt-0.5 block truncate text-[10px] font-semibold text-muted">{state}</span>
    </div>
  );
}

function MiniKpi({ label, value }: { label: string; value: number }) {
  return (
    <div className="min-w-[74px] rounded-md border border-line bg-white/80 px-2 py-1.5 text-right">
      <p className="text-base font-bold leading-none text-ink">{value}</p>
      <p className="mt-1 text-[10px] font-bold uppercase tracking-wide text-muted">{label}</p>
    </div>
  );
}

function DashboardLoading() {
  const [isSlow, setIsSlow] = useState(false);

  useEffect(() => {
    const id = window.setTimeout(() => setIsSlow(true), 1500);
    return () => window.clearTimeout(id);
  }, []);

  return (
    <div className="h-screen overflow-hidden p-3">
      <Card>
        <CardBody className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-bold text-ink">{isSlow ? "Still connecting to the demo workspace" : "Loading dashboard"}</p>
            <p className="mt-1 text-sm text-muted">
              {isSlow ? "If this stays here, the local API or demo cookie needs a refresh." : "Preparing trainer workspace..."}
            </p>
          </div>
          {isSlow && (
            <a className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white" href={routes.login}>
              Go to login
            </a>
          )}
        </CardBody>
      </Card>
    </div>
  );
}

function DashboardError({ error, isRetrying, onRetry }: { error: unknown; isRetrying: boolean; onRetry: () => void }) {
  return (
    <div className="flex h-screen items-center justify-center overflow-hidden p-6">
      <Card className="max-w-md">
        <CardBody className="space-y-4">
          <AlertCircle className="text-danger" />
          <div>
            <p className="font-bold text-ink">Dashboard could not load</p>
            <p className="mt-1 text-sm text-muted">{getErrorMessage(error)}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-panel"
              type="button"
              onClick={onRetry}
            >
              <RotateCw size={16} />
              {isRetrying ? "Retrying..." : "Retry"}
            </button>
            <a className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700" href={routes.login}>
              Go to login
            </a>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
