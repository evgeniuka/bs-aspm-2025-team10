"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, BarChart3, Clock, Dumbbell } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";
import { api } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { routes } from "@/lib/routes";
import { Card, CardBody } from "@/components/ui/card";
import { SessionSummaryCard } from "@/components/sessions/session-summary-card";

export function SessionSummaryView({ sessionId }: { sessionId: number }) {
  const queryClient = useQueryClient();
  const [savingClientId, setSavingClientId] = useState<number | null>(null);
  const { data, isLoading, error } = useQuery({
    queryKey: ["session-summary", sessionId],
    queryFn: () => api.sessionSummary(sessionId)
  });

  const updateSummary = useMutation({
    mutationFn: ({
      clientId,
      payload
    }: {
      clientId: number;
      payload: { coach_notes: string | null; next_focus: string | null };
    }) => api.updateSessionClientSummary(sessionId, clientId, payload),
    onMutate: ({ clientId }) => setSavingClientId(clientId),
    onSuccess: (summary) => {
      queryClient.setQueryData(["session-summary", sessionId], summary);
      summary.clients.forEach((client) => {
        void queryClient.invalidateQueries({ queryKey: ["client-detail", client.client_id] });
      });
    },
    onSettled: () => setSavingClientId(null)
  });

  if (isLoading) {
    return <div className="page-wrap text-sm text-muted">Loading session summary...</div>;
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <Card className="max-w-md">
          <CardBody className="space-y-4">
            <p className="text-sm text-muted">Could not load this session summary.</p>
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

  return (
    <div className="page-wrap">
      <header className="page-titlebar flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-muted">Session summary</p>
          <h1 className="text-3xl font-bold text-ink">Session #{data.session_id}</h1>
          <p className="mt-1 text-sm text-muted">
            {formatDate(data.ended_at ?? data.started_at)} - volume is calculated from actual logged reps and weight
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
        <SummaryMetric icon={<Dumbbell size={18} />} label="Clients" value={String(data.total_clients)} />
        <SummaryMetric icon={<BarChart3 size={18} />} label="Sets" value={`${data.total_sets_completed}/${data.total_planned_sets}`} />
        <SummaryMetric icon={<BarChart3 size={18} />} label="Actual volume" value={`${data.total_volume_kg}kg`} />
        <SummaryMetric icon={<Clock size={18} />} label="Duration" value={formatDuration(data.duration_minutes)} />
      </section>

      <section className="space-y-4">
        {data.clients.map((client) => (
          <SessionSummaryCard
            client={client}
            isSaving={savingClientId === client.client_id}
            key={client.client_id}
            onSave={(clientId, payload) => updateSummary.mutate({ clientId, payload })}
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
