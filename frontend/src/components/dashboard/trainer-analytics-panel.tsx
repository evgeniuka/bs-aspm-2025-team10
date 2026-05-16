"use client";

import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { TrainerAnalytics } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export function TrainerAnalyticsPanel() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["trainer-analytics"],
    queryFn: api.trainerAnalytics
  });

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <p className="text-sm text-muted">Loading analytics...</p>
        </CardBody>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card>
        <CardBody>
          <p className="text-sm text-danger">{getErrorMessage(error)}</p>
        </CardBody>
      </Card>
    );
  }

  return <TrainerAnalyticsCard analytics={data} />;
}

export function TrainerAnalyticsCard({ analytics }: { analytics: TrainerAnalytics }) {
  const dailyData = analytics.volume_by_day
    .filter((point) => point.volume_kg > 0)
    .map((point) => ({
      date: formatDate(point.date),
      volume: point.volume_kg,
      sets: point.sets_completed
    }));
  const weeklyData = analytics.weekly_volume.map((point) => ({
    week: formatDate(point.week_start),
    volume: point.volume_kg,
    sets: point.sets_completed,
    sessions: point.sessions
  }));
  const maxReadiness = Math.max(...analytics.readiness_mix.map((item) => item.clients), 1);

  return (
    <Card>
      <CardHeader className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-ink">Trainer analytics</h2>
          <p className="text-xs text-muted">{analytics.total_sessions} sessions in the demo workspace</p>
        </div>
        <span className="rounded-full bg-panel px-3 py-1 text-xs font-bold uppercase text-muted">
          {analytics.completion_rate}% set completion
        </span>
      </CardHeader>
      <CardBody className="space-y-4">
        <div className="grid gap-3 md:grid-cols-4">
          <AnalyticsMetric label="Volume" value={`${analytics.total_volume_kg}kg`} />
          <AnalyticsMetric label="Sets" value={`${analytics.total_sets_completed}/${analytics.total_planned_sets}`} />
          <AnalyticsMetric label="Avg sets" value={String(analytics.average_sets_per_session)} />
          <AnalyticsMetric label="Avg session" value={formatDuration(analytics.average_session_minutes)} />
        </div>

        <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="min-h-72 rounded-md border border-line p-3">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-bold text-ink">Daily volume</p>
                <p className="text-xs text-muted">Actual logged reps x weight</p>
              </div>
              <span className="status-pill">{analytics.completed_sessions} completed</span>
            </div>
            {dailyData.length === 0 ? (
              <div className="flex h-64 items-center justify-center rounded-md border border-dashed border-line bg-panel text-sm font-semibold text-muted">
                No workout volume yet
              </div>
            ) : dailyData.length === 1 ? (
              <SingleDayVolume date={dailyData[0].date} sets={dailyData[0].sets} volume={dailyData[0].volume} />
            ) : (
              <ResponsiveContainer height={260} width="100%">
                <BarChart data={dailyData}>
                  <CartesianGrid stroke="#d9e0ea" vertical={false} />
                  <XAxis dataKey="date" tickLine={false} />
                  <YAxis tickLine={false} width={48} />
                  <Tooltip
                    cursor={false}
                    contentStyle={{ borderColor: "#d9e0ea", borderRadius: 8 }}
                    formatter={(value, name) => [name === "volume" ? `${value}kg` : value, name === "volume" ? "Volume" : "Sets"]}
                  />
                  <Bar barSize={56} dataKey="volume" fill="#2563eb" minPointSize={4} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="grid gap-4">
            <PanelBlock title="Readiness today" subtitle="Check-ins and missing signals">
              <div className="space-y-2">
                {analytics.readiness_mix.map((item) => (
                  <div className="grid grid-cols-[86px_1fr_34px] items-center gap-2 text-sm" key={item.status}>
                    <span className="font-semibold capitalize text-ink">{item.status}</span>
                    <span className="h-2 overflow-hidden rounded-full bg-slate-200">
                      <span className={`block h-full rounded-full ${readinessColor(item.status)}`} style={{ width: `${(item.clients / maxReadiness) * 100}%` }} />
                    </span>
                    <span className="text-right font-bold text-muted">{item.clients}</span>
                  </div>
                ))}
              </div>
            </PanelBlock>

            <PanelBlock title="Weekly trend" subtitle="Workload by training week">
              {weeklyData.length === 0 ? (
                <p className="rounded-md border border-dashed border-line bg-panel p-4 text-sm font-semibold text-muted">No weekly trend yet</p>
              ) : (
                <ResponsiveContainer height={170} width="100%">
                  <LineChart data={weeklyData}>
                    <CartesianGrid stroke="#d9e0ea" vertical={false} />
                    <XAxis dataKey="week" tickLine={false} />
                    <YAxis tickLine={false} width={44} />
                    <Tooltip contentStyle={{ borderColor: "#d9e0ea", borderRadius: 8 }} formatter={(value) => [`${value}kg`, "Volume"]} />
                    <Line dataKey="volume" dot={{ fill: "#0f766e", r: 4 }} stroke="#0f766e" strokeWidth={3} type="monotone" />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </PanelBlock>
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
          <PanelBlock title="Focus mix" subtitle="Where coaching time is going">
            <div className="space-y-2">
              {analytics.focus_mix.map((focus) => (
                <div className="rounded-md border border-line bg-white/80 px-3 py-2" key={focus.focus}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-bold text-ink">{focus.focus}</p>
                    <span className="text-xs font-bold text-muted">{focus.completion_rate}% complete</span>
                  </div>
                  <p className="mt-1 text-xs text-muted">
                    {focus.client_sessions} client sessions / {focus.sets_completed} of {focus.planned_sets} sets / {focus.volume_kg}kg
                  </p>
                </div>
              ))}
            </div>
          </PanelBlock>

          <PanelBlock title="Top exercises" subtitle="Most loaded movements by actual logs">
            <div className="overflow-hidden rounded-md border border-line">
              <div className="grid grid-cols-[1fr_70px_78px_60px] bg-panel px-3 py-2 text-xs font-bold uppercase text-muted">
                <span>Exercise</span>
                <span className="text-right">Sets</span>
                <span className="text-right">Volume</span>
                <span className="text-right">Clients</span>
              </div>
              {analytics.top_exercises.map((exercise) => (
                <div className="grid grid-cols-[1fr_70px_78px_60px] items-center border-t border-line px-3 py-2 text-sm" key={exercise.exercise_id}>
                  <span className="font-semibold text-ink">{exercise.exercise_name}</span>
                  <span className="text-right text-muted">{exercise.sets_completed}</span>
                  <span className="text-right font-semibold text-ink">{exercise.volume_kg}kg</span>
                  <span className="text-right text-muted">{exercise.clients}</span>
                </div>
              ))}
            </div>
          </PanelBlock>
        </div>

        <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <PanelBlock title="Client load" subtitle="Volume and adherence by client">
            <div className="overflow-hidden rounded-md border border-line">
              <div className="grid grid-cols-[1fr_88px_88px] bg-panel px-3 py-2 text-xs font-bold uppercase text-muted">
                <span>Client</span>
                <span className="text-right">Volume</span>
                <span className="text-right">Complete</span>
              </div>
              {analytics.client_load.map((client) => (
                <a
                  className="grid grid-cols-[1fr_88px_88px] items-center border-t border-line px-3 py-2 text-sm transition hover:bg-panel"
                  href={routes.client(client.client_id)}
                  key={client.client_id}
                >
                  <span>
                    <span className="block font-semibold text-ink">{client.client_name}</span>
                    <span className="text-xs text-muted">{client.sessions} sessions</span>
                  </span>
                  <span className="text-right font-semibold text-ink">{client.volume_kg}kg</span>
                  <span className="text-right text-muted">{client.completion_rate}%</span>
                </a>
              ))}
            </div>
          </PanelBlock>

          <PanelBlock title="Coach attention" subtitle="Who may need a quick decision before training">
            <div className="space-y-2">
              {analytics.attention_clients.map((client) => (
                <a className="block rounded-md border border-line bg-white/80 px-3 py-2 transition hover:bg-panel" href={routes.client(client.client_id)} key={client.client_id}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-bold text-ink">{client.client_name}</p>
                    <span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase ${readinessPill(client.readiness_status)}`}>{client.readiness_status}</span>
                  </div>
                  <p className="mt-1 text-xs text-muted">
                    {client.risk_flags.join(", ")} / {client.completion_rate}% completion
                    {client.days_since_last_workout !== null ? ` / ${client.days_since_last_workout}d since last` : ""}
                  </p>
                </a>
              ))}
              {analytics.attention_clients.length === 0 ? <p className="rounded-md border border-dashed border-line bg-panel p-4 text-sm font-semibold text-muted">No attention flags today</p> : null}
            </div>
          </PanelBlock>
        </div>
      </CardBody>
    </Card>
  );
}

function SingleDayVolume({ date, sets, volume }: { date: string; sets: number; volume: number }) {
  return (
    <div className="flex h-64 flex-col justify-between rounded-md bg-panel p-4">
      <div>
        <p className="text-xs font-bold uppercase tracking-wide text-muted">Recorded volume</p>
        <p className="mt-2 text-3xl font-bold text-ink">{volume}kg</p>
        <p className="mt-1 text-sm text-muted">
          {sets} completed sets on {date}
        </p>
      </div>
      <div>
        <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase text-muted">
          <span>Demo workload</span>
          <span>single training day</span>
        </div>
        <div className="h-3 rounded-full bg-white">
          <div className="h-3 w-full rounded-full bg-brand" />
        </div>
      </div>
    </div>
  );
}

function AnalyticsMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <p className="text-xs font-semibold uppercase text-muted">{label}</p>
      <p className="mt-1 text-lg font-bold text-ink">{value}</p>
    </div>
  );
}

function PanelBlock({ children, subtitle, title }: { children: ReactNode; subtitle: string; title: string }) {
  return (
    <section className="rounded-md border border-line bg-white/70 p-3">
      <div className="mb-3">
        <h3 className="text-sm font-bold text-ink">{title}</h3>
        <p className="text-xs text-muted">{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

function readinessColor(status: string) {
  if (status === "attention") return "bg-danger";
  if (status === "caution") return "bg-warning";
  if (status === "missing") return "bg-slate-400";
  return "bg-success";
}

function readinessPill(status: string) {
  if (status === "attention") return "bg-red-50 text-danger";
  if (status === "caution") return "bg-amber-50 text-warning";
  if (status === "missing") return "bg-slate-100 text-muted";
  return "bg-emerald-50 text-success";
}
