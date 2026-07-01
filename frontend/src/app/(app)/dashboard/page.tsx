"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BarChart3, CalendarDays, ClipboardList, Play, RotateCw, Users } from "lucide-react";
import type { ReactNode } from "react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import { Card, CardBody } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

const READINESS = {
  ready: { label: "Ready", dot: "bg-success", pill: "bg-success-soft text-success" },
  caution: { label: "Caution", dot: "bg-warning", pill: "bg-warning-soft text-warning" },
  attention: { label: "Attention", dot: "bg-danger", pill: "bg-danger-soft text-danger" },
  missing: { label: "No check-in", dot: "bg-line", pill: "bg-panel text-muted" }
} as const;

export default function DashboardPage() {
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.dashboard,
    retry: false
  });

  if (isLoading) {
    return <div className="page-wrap text-sm text-muted">Loading your workspace...</div>;
  }
  if (error || !data) {
    return (
      <div className="page-wrap">
        <Card className="max-w-md">
          <CardBody className="space-y-4">
            <p className="font-medium text-ink">Your dashboard could not load</p>
            <p className="text-sm text-muted">{getErrorMessage(error)}</p>
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-line bg-white px-4 py-2 text-sm font-medium text-ink transition hover:bg-panel"
              type="button"
              onClick={() => refetch()}
            >
              <RotateCw size={16} />
              {isRefetching ? "Retrying..." : "Try again"}
            </button>
          </CardBody>
        </Card>
      </div>
    );
  }

  const active = data.active_session;
  const readiness = data.today_readiness;
  const readyCount = readiness.filter((item) => item.readiness_status === "ready").length;

  return (
    <div className="page-wrap max-w-[1040px]">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Trainer dashboard</h1>
          <p className="mt-1 text-sm text-muted">{active ? "A live session is running." : "Pick up where today's coaching begins."}</p>
        </div>
        <span className={`status-pill ${active ? "border-success-soft bg-success-soft text-success" : ""}`}>
          {active ? "Live session active" : "No active session"}
        </span>
      </header>

      <section className="visual-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-5">
          <div>
            <p className="field-label">Today&apos;s session</p>
            {active ? (
              <p className="mt-1 text-[26px] font-semibold leading-tight text-ink">Session #{active.id} in progress</p>
            ) : (
              <p className="mt-1 text-[26px] font-semibold leading-tight text-ink">
                {readyCount} of {readiness.length} clients ready
              </p>
            )}
            <div className="mt-3 flex gap-1.5">
              {readiness.slice(0, 12).map((item) => (
                <span aria-hidden="true" className={`h-3.5 w-3.5 rounded-full ${READINESS[item.readiness_status].dot}`} key={item.client.id} />
              ))}
            </div>
          </div>
          <div className="flex min-w-[180px] flex-col gap-2">
            {active ? (
              <a
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-brand px-4 text-sm font-medium text-white transition hover:bg-blue-700"
                href={routes.session(active.id)}
              >
                <Play size={16} />
                Resume cockpit
              </a>
            ) : (
              <a
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-brand px-4 text-sm font-medium text-white transition hover:bg-blue-700"
                href={routes.newSession}
              >
                <Play size={16} />
                Start a session
              </a>
            )}
            <a
              className="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg border border-line bg-white px-4 text-sm font-medium text-ink transition hover:bg-panel"
              href={routes.newProgram}
            >
              Build a program
            </a>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardBody>
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-base font-semibold text-ink">Today&apos;s clients</h2>
              <a className="text-sm font-medium text-brand" href={routes.clients}>
                View all
              </a>
            </div>
            <div>
              {readiness.length === 0 ? <p className="py-4 text-sm text-muted">No active clients yet.</p> : null}
              {readiness.slice(0, 6).map((item) => (
                <a
                  className="flex items-center gap-3 border-b border-line py-2.5 last:border-b-0"
                  href={routes.client(item.client.id)}
                  key={item.client.id}
                >
                  <ClientAvatar name={item.client.name} size="sm" />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium text-ink">{item.client.name}</span>
                    <span className="block truncate text-xs text-muted">{subtext(item)}</span>
                  </span>
                  <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${READINESS[item.readiness_status].pill}`}>
                    {READINESS[item.readiness_status].label}
                  </span>
                </a>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <h2 className="mb-2 text-base font-semibold text-ink">Recent sessions</h2>
            <div>
              {data.recent_sessions.length === 0 ? <p className="py-4 text-sm text-muted">No sessions logged yet.</p> : null}
              {data.recent_sessions.slice(0, 5).map((session) => (
                <a
                  className="flex items-center gap-3 border-b border-line py-2.5 last:border-b-0"
                  href={routes.sessionSummary(session.id)}
                  key={session.id}
                >
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-panel text-muted">
                    <CalendarDays size={15} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium text-ink">Session #{session.id}</span>
                    <span className="block text-xs text-muted">
                      {formatDate(session.ended_at ?? session.started_at)} · {session.clients.length} clients
                    </span>
                  </span>
                  <ArrowRight className="shrink-0 text-faint" size={16} />
                </a>
              ))}
            </div>
          </CardBody>
        </Card>
      </section>

      <section className="grid grid-cols-3 gap-4">
        <Metric icon={<Users size={16} />} label="Clients" value={data.total_clients} />
        <Metric icon={<ClipboardList size={16} />} label="Programs" value={data.total_programs} />
        <Metric icon={<BarChart3 size={16} />} label="Sessions done" value={data.completed_sessions} />
      </section>
    </div>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-xl bg-panel px-4 py-3.5">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted">{label}</p>
        <span className="text-faint">{icon}</span>
      </div>
      <p className="mt-1 text-2xl font-semibold text-ink">{value}</p>
    </div>
  );
}

function subtext(item: { client: { fitness_level: string }; check_in: unknown; risk_flags: string[] }) {
  if (!item.check_in) return `${item.client.fitness_level} · no check-in yet`;
  if (item.risk_flags.length > 0) return `${item.client.fitness_level} · ${item.risk_flags.join(", ")}`;
  return item.client.fitness_level;
}
