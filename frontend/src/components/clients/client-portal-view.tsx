"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, ArrowRight, BarChart3, CalendarDays, CheckCircle2, ClipboardList, HeartPulse, LogOut, Moon, Target } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";
import { api } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { ClientCheckIn, Program } from "@/lib/types";
import { ClientAnalyticsChart } from "@/components/clients/client-analytics-chart";
import { ClientHistoryList } from "@/components/clients/client-history-list";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";
import { BrandMark } from "@/components/ui/brand-mark";
import { plannedProgramStats } from "@/components/dashboard/session-setup-model";

export function ClientPortalView() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["trainee-me"],
    queryFn: api.traineeMe,
    retry: false
  });
  const logout = useMutation({
    mutationFn: api.logout,
    onSettled: () => window.location.assign(routes.login)
  });

  if (isLoading) {
    return <div className="page-wrap text-sm text-muted">Loading client portal...</div>;
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <Card className="max-w-md">
          <CardBody className="space-y-4">
            <p className="font-bold text-ink">Client portal could not load</p>
            <p className="text-sm text-muted">{getErrorMessage(error)}</p>
            <a className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white" href={routes.login}>
              Go to login
            </a>
          </CardBody>
        </Card>
      </div>
    );
  }

  const { analytics, client, programs, recent_sessions: recentSessions } = data;
  const latestSession = recentSessions[0] ?? null;
  const primaryProgram = programs[0] ?? null;

  return (
    <main className="min-h-screen">
      <header className="border-b border-white/70 bg-white/90 px-4 py-3 shadow-[0_1px_2px_rgba(17,24,39,0.04)] backdrop-blur">
        <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <BrandMark />
            <div>
              <p className="field-label">FitCoach Client</p>
              <h1 className="text-base font-bold text-ink">Training Hub</h1>
            </div>
          </div>
          <Button disabled={logout.isPending} variant="secondary" onClick={() => logout.mutate()}>
            <LogOut size={16} />
            Sign out
          </Button>
        </div>
      </header>

      <div className="page-wrap">
        <section className="visual-card grid gap-4 p-4 lg:grid-cols-[1fr_340px]">
          <div className="flex min-w-0 items-center gap-4">
            <ClientAvatar name={client.name} size="lg" />
            <div className="min-w-0">
              <p className="field-label">Your training workspace</p>
              <h2 className="truncate text-3xl font-bold text-ink">{client.name}</h2>
              <p className="mt-1 max-w-3xl text-sm leading-6 text-muted">{client.goals}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <HeroFact label="Level" value={client.fitness_level} />
            <HeroFact label="Last workout" value={client.last_workout_date ? formatDate(client.last_workout_date) : "Not yet"} />
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-4">
          <PortalMetric icon={<Activity size={18} />} label="Sessions" value={String(analytics.total_sessions)} />
          <PortalMetric icon={<ClipboardList size={18} />} label="Sets" value={String(analytics.total_sets)} />
          <PortalMetric icon={<BarChart3 size={18} />} label="Volume" value={`${analytics.total_volume_kg}kg`} />
          <PortalMetric icon={<CalendarDays size={18} />} label="Avg duration" value={formatDuration(analytics.average_session_minutes)} />
        </section>

        <section className="grid gap-4 xl:grid-cols-[1fr_400px]">
          <ClientAnalyticsChart analytics={analytics} />
          <div className="grid gap-4">
            <ClientCheckInCard checkIn={data.today_check_in} key={data.today_check_in?.updated_at ?? "empty-check-in"} />
            <Card>
              <CardHeader>
                <h2 className="text-base font-bold text-ink">From your coach</h2>
              </CardHeader>
              <CardBody className="space-y-3">
                <CoachNote label="Next focus" value={latestSession?.next_focus ?? "Your coach has not set the next focus yet."} />
                <CoachNote label="Last note" value={latestSession?.coach_notes ?? "No coach note yet."} />
                {latestSession && (
                  <a className="inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800" href={routes.clientSessionSummary(latestSession.session_id)}>
                    Open latest session
                    <ArrowRight size={16} />
                  </a>
                )}
              </CardBody>
            </Card>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
          <Card>
            <CardHeader className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-bold text-ink">Your programs</h2>
                <p className="text-xs text-muted">{programs.length} active training plans</p>
              </div>
              {primaryProgram && <span className="status-pill">{primaryProgram.focus ?? "custom"}</span>}
            </CardHeader>
            <CardBody className="space-y-3">
              {programs.map((program) => (
                <ProgramCard key={program.id} program={program} />
              ))}
              {programs.length === 0 && <p className="text-sm text-muted">No programs assigned yet.</p>}
            </CardBody>
          </Card>

          <ClientHistoryList sessionHref={routes.clientSessionSummary} sessions={recentSessions} />
        </section>
      </div>
    </main>
  );
}

function ClientCheckInCard({ checkIn }: { checkIn: ClientCheckIn | null }) {
  const queryClient = useQueryClient();
  const [energyLevel, setEnergyLevel] = useState(checkIn?.energy_level ?? 4);
  const [sleepQuality, setSleepQuality] = useState(checkIn?.sleep_quality ?? 4);
  const [sorenessLevel, setSorenessLevel] = useState(checkIn?.soreness_level ?? 1);
  const [painNotes, setPainNotes] = useState(checkIn?.pain_notes ?? "");
  const [trainingGoal, setTrainingGoal] = useState(checkIn?.training_goal ?? "");
  const save = useMutation({
    mutationFn: () =>
      api.upsertTraineeCheckIn({
        energy_level: energyLevel,
        sleep_quality: sleepQuality,
        soreness_level: sorenessLevel,
        pain_notes: painNotes,
        training_goal: trainingGoal
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainee-me"] });
    }
  });

  const status = save.data?.readiness_status ?? checkIn?.readiness_status ?? "ready";

  return (
    <Card className="border-brand/20">
      <CardHeader className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-ink">Today check-in</h2>
          <p className="text-xs text-muted">{checkIn ? `Submitted ${formatDate(checkIn.submitted_on)}` : "Not submitted yet"}</p>
        </div>
        <span className={checkInStatusClass(status)}>{status}</span>
      </CardHeader>
      <CardBody className="space-y-3">
        <ScorePicker icon={<HeartPulse size={15} />} label="Energy" value={energyLevel} onChange={setEnergyLevel} />
        <ScorePicker icon={<Moon size={15} />} label="Sleep" value={sleepQuality} onChange={setSleepQuality} />
        <ScorePicker icon={<Activity size={15} />} label="Soreness" max={5} min={0} value={sorenessLevel} onChange={setSorenessLevel} />
        <label className="block">
          <span className="field-label">Pain / limitations</span>
          <textarea
            aria-label="Pain or limitation notes"
            className="field-control min-h-20 resize-none"
            maxLength={500}
            value={painNotes}
            onChange={(event) => setPainNotes(event.target.value)}
          />
        </label>
        <label className="block">
          <span className="field-label">Goal today</span>
          <input
            aria-label="Training goal for today"
            className="field-control"
            maxLength={220}
            value={trainingGoal}
            onChange={(event) => setTrainingGoal(event.target.value)}
          />
        </label>
        {save.error && <p className="rounded-md bg-red-50 p-2 text-sm text-danger">{getErrorMessage(save.error)}</p>}
        {save.isSuccess && (
          <p className="flex items-center gap-2 rounded-md bg-emerald-50 p-2 text-sm font-semibold text-success">
            <CheckCircle2 size={16} />
            Check-in saved
          </p>
        )}
        <Button className="w-full" disabled={save.isPending} onClick={() => save.mutate()}>
          <Target size={16} />
          {save.isPending ? "Saving..." : "Save check-in"}
        </Button>
      </CardBody>
    </Card>
  );
}

function ScorePicker({
  icon,
  label,
  max = 5,
  min = 1,
  value,
  onChange
}: {
  icon: ReactNode;
  label: string;
  max?: number;
  min?: number;
  value: number;
  onChange: (value: number) => void;
}) {
  const values = Array.from({ length: max - min + 1 }, (_, index) => min + index);
  return (
    <div>
      <div className="mb-1.5 flex items-center gap-2">
        <span className="text-brand">{icon}</span>
        <p className="field-label">{label}</p>
      </div>
      <div className="grid overflow-hidden rounded-md border border-line bg-white" style={{ gridTemplateColumns: `repeat(${values.length}, minmax(0, 1fr))` }}>
        {values.map((score) => (
          <button
            aria-label={`${label} ${score}`}
            aria-pressed={score === value}
            className={`min-h-9 border-r border-line text-sm font-bold transition last:border-r-0 ${
              score === value ? "bg-ink text-white" : "bg-white text-muted hover:bg-panel hover:text-ink"
            }`}
            key={score}
            type="button"
            onClick={() => onChange(score)}
          >
            {score}
          </button>
        ))}
      </div>
    </div>
  );
}

function ProgramCard({ program }: { program: Program }) {
  const stats = plannedProgramStats(program);
  return (
    <article className="rounded-md border border-line bg-white/80 px-3 py-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-bold text-ink">{program.name}</p>
          <p className="mt-1 text-xs text-muted">
            {stats.sets} sets / {stats.volumeKg}kg planned
          </p>
        </div>
        <span className="rounded-full border border-line bg-panel px-2 py-1 text-[10px] font-bold uppercase text-muted">{program.focus ?? "Custom"}</span>
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {program.exercises.slice(0, 5).map((exercise) => (
          <span className="rounded-full bg-panel px-2 py-1 text-xs font-semibold text-muted" key={exercise.id}>
            {exercise.exercise.name}
          </span>
        ))}
      </div>
    </article>
  );
}

function PortalMetric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
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

function HeroFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="surface-panel p-3">
      <p className="field-label">{label}</p>
      <p className="mt-1 text-sm font-bold text-ink">{value}</p>
    </div>
  );
}

function CoachNote({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <p className="field-label">{label}</p>
      <p className="mt-1 text-sm font-semibold leading-6 text-ink">{value}</p>
    </div>
  );
}

function checkInStatusClass(status: ClientCheckIn["readiness_status"]) {
  const base = "rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase";
  if (status === "attention") return `${base} border-red-200 bg-red-50 text-danger`;
  if (status === "caution") return `${base} border-amber-200 bg-amber-50 text-warning`;
  return `${base} border-emerald-200 bg-emerald-50 text-success`;
}
