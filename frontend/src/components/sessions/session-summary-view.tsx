"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, BarChart3, Clock, Dumbbell, Users } from "lucide-react";
import type { ReactNode } from "react";
import { api } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import { Card, CardBody } from "@/components/ui/card";
import { SessionSummaryCard, type SessionSummaryNotes } from "@/components/sessions/session-summary-card";

export function SessionSummaryView({ sessionId }: { sessionId: number }) {
  const queryClient = useQueryClient();
  const { data, error, isLoading } = useQuery({
    queryKey: ["session-summary", sessionId],
    queryFn: () => api.sessionSummary(sessionId),
    retry: false
  });
  const save = useMutation({
    mutationFn: ({ clientId, payload }: { clientId: number; payload: SessionSummaryNotes }) =>
      api.updateSessionClientSummary(sessionId, clientId, payload),
    onSuccess: (summary) => {
      queryClient.setQueryData(["session-summary", sessionId], summary);
    }
  });

  if (isLoading) {
    return <div className="page-wrap text-sm text-muted">Loading session summary...</div>;
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <Card className="max-w-md">
          <CardBody className="space-y-4">
            <p className="font-bold text-ink">Session summary could not load</p>
            <p className="text-sm text-muted">{getErrorMessage(error)}</p>
            <a className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white" href={routes.dashboard}>
              Back to dashboard
            </a>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="page-wrap">
      <header className="page-titlebar flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="field-label">Session summary</p>
          <h1 className="text-3xl font-bold text-ink">Session #{data.session_id}</h1>
          <p className="mt-1 text-sm text-muted">
            {formatDate(data.ended_at ?? data.started_at)} - {data.status}
          </p>
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
        <SummaryMetric icon={<Users size={18} />} label="Clients" value={String(data.total_clients)} />
        <SummaryMetric icon={<BarChart3 size={18} />} label="Sets" value={`${data.total_sets_completed}/${data.total_planned_sets}`} />
        <SummaryMetric icon={<Dumbbell size={18} />} label="Volume" value={`${data.total_volume_kg}kg`} />
        <SummaryMetric icon={<Clock size={18} />} label="Duration" value={formatDuration(data.duration_minutes)} />
      </section>

      {save.error && <p className="rounded-md bg-red-50 p-3 text-sm font-semibold text-danger">{getErrorMessage(save.error)}</p>}

      <section className="grid gap-4 lg:grid-cols-2">
        {data.clients.map((client) => (
          <SessionSummaryCard
            client={client}
            clientHref={routes.client(client.client_id)}
            isSaving={save.isPending && save.variables?.clientId === client.client_id}
            key={client.client_id}
            onSave={(payload) => save.mutate({ clientId: client.client_id, payload })}
          />
        ))}
      </section>
    </div>
  );
}

function SummaryMetric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
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
