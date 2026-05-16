"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BarChart3, Clock, Dumbbell } from "lucide-react";
import type { ReactNode } from "react";
import { api } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { routes } from "@/lib/routes";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";
import { ClientAnalyticsChart } from "@/components/clients/client-analytics-chart";
import { ClientHistoryList } from "@/components/clients/client-history-list";

export function ClientProfileView({ clientId }: { clientId: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["client-detail", clientId],
    queryFn: () => api.clientDetail(clientId)
  });

  if (isLoading) {
    return <div className="page-wrap text-sm text-muted">Loading client profile...</div>;
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <Card className="max-w-md">
          <CardBody className="space-y-4">
            <p className="text-sm text-muted">Could not load this client profile.</p>
            <a
              className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              href={routes.dashboard}
            >
              Back to dashboard
            </a>
          </CardBody>
        </Card>
      </div>
    );
  }

  const { client, analytics, programs, recent_sessions: recentSessions } = data;

  return (
    <div className="page-wrap">
      <header className="page-titlebar visual-card flex flex-wrap items-end justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4">
          <ClientAvatar name={client.name} size="lg" />
          <div className="min-w-0">
            <p className="text-xs font-bold uppercase tracking-wide text-muted">Client profile</p>
            <h1 className="truncate text-3xl font-bold text-ink">{client.name}</h1>
            <p className="mt-1 max-w-3xl text-sm text-muted">
              {client.fitness_level} - {client.goals}
            </p>
          </div>
        </div>
        <a
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-panel"
          href={routes.dashboard}
        >
          <ArrowLeft size={16} />
          Back to dashboard
        </a>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        <ProfileMetric icon={<Dumbbell size={18} />} label="Sessions" value={String(analytics.total_sessions)} />
        <ProfileMetric icon={<BarChart3 size={18} />} label="Sets" value={String(analytics.total_sets)} />
        <ProfileMetric icon={<BarChart3 size={18} />} label="Volume" value={`${analytics.total_volume_kg}kg`} />
        <ProfileMetric icon={<Clock size={18} />} label="Avg duration" value={formatDuration(analytics.average_session_minutes)} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_360px]">
        <ClientAnalyticsChart analytics={analytics} />
        <Card>
          <CardHeader>
            <h2 className="text-base font-bold text-ink">Client status</h2>
          </CardHeader>
          <CardBody className="space-y-3 text-sm">
            <StatusRow label="Last workout" value={client.last_workout_date ? formatDate(client.last_workout_date) : "No workout yet"} />
            <StatusRow label="Completed sessions" value={String(analytics.completed_sessions)} />
            <StatusRow label="Active programs" value={String(programs.length)} />
          </CardBody>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_0.8fr]">
        <ClientHistoryList sessions={recentSessions} />
        <Card>
          <CardHeader>
            <h2 className="text-base font-bold text-ink">Programs</h2>
          </CardHeader>
          <CardBody className="space-y-3">
            {programs.map((program) => (
              <a className="block rounded-md border border-line px-3 py-2 transition hover:bg-panel" href={routes.program(program.id)} key={program.id}>
                <p className="text-sm font-bold text-ink">{program.name}</p>
                <p className="text-xs text-muted">{program.exercises.length} exercises</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {program.exercises.slice(0, 4).map((exercise) => (
                    <span className="rounded-full bg-panel px-2 py-1 text-xs font-semibold text-muted" key={exercise.id}>
                      {exercise.exercise.name}
                    </span>
                  ))}
                </div>
              </a>
            ))}
            {programs.length === 0 && <p className="text-sm text-muted">No programs created yet.</p>}
          </CardBody>
        </Card>
      </section>
    </div>
  );
}

function ProfileMetric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <Card>
      <CardBody className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase text-muted">{label}</p>
          <p className="mt-1 text-2xl font-bold text-ink">{value}</p>
        </div>
        <span className="rounded-md bg-panel p-2 text-brand">{icon}</span>
      </CardBody>
    </Card>
  );
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-line pb-2 last:border-0 last:pb-0">
      <span className="text-muted">{label}</span>
      <span className="font-semibold text-ink">{value}</span>
    </div>
  );
}
