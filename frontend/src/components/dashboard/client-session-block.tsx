"use client";

import { CalendarDays, ClipboardList, ExternalLink, Target } from "lucide-react";
import type { ReactNode } from "react";
import { formatDate } from "@/lib/format";
import { routes } from "@/lib/routes";
import { ClientAvatar } from "@/components/ui/client-avatar";
import { plannedProgramStats, programVariantName, type SessionAssignment } from "@/components/dashboard/session-setup-model";

export function ClientSessionBlock({ assignments }: { assignments: SessionAssignment[] }) {
  return (
    <section className="rounded-md border border-line bg-white/70 p-2.5">
      <div className="mb-2 flex items-center justify-between gap-3">
        <div>
          <p className="field-label">Client block</p>
          <p className="text-xs text-muted">{assignments.length === 0 ? "Select a client to prepare the session." : "Context for the opening lineup."}</p>
        </div>
        <span className="rounded-full border border-line bg-white px-2.5 py-1 text-xs font-bold text-muted">
          {assignments.length || "0"} selected
        </span>
      </div>

      {assignments.length === 0 ? (
        <div className="surface-panel grid grid-cols-[38px_1fr] items-center gap-3 p-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-panel text-brand">
            <Target size={16} />
          </span>
          <span>
            <span className="block text-sm font-bold text-ink">No client selected</span>
            <span className="block text-xs text-muted">Pick from the roster to show goals and plan fit.</span>
          </span>
        </div>
      ) : (
        <div className="grid gap-2 min-[900px]:grid-cols-2">
          {assignments.map((assignment) => (
            <ClientContextCard assignment={assignment} key={assignment.client.id} />
          ))}
        </div>
      )}
    </section>
  );
}

function ClientContextCard({ assignment }: { assignment: SessionAssignment }) {
  const { client, program } = assignment;
  const stats = plannedProgramStats(program);
  const lastWorkout = client.last_workout_date ? formatDate(client.last_workout_date) : "No workout yet";
  const exercises = program.exercises.slice(0, 3);

  return (
    <article className="surface-panel min-w-0 p-2.5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2.5">
          <ClientAvatar name={client.name} size="sm" />
          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-ink">{client.name}</p>
            <p className="truncate text-xs text-muted">{client.fitness_level}</p>
          </div>
        </div>
        <span className={focusClassName(program.focus)}>{program.focus ?? "Custom"}</span>
      </div>

      <div className="mt-2 rounded-md bg-panel/80 p-2">
        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wide text-muted">
          <Target size={12} />
          Goal
        </div>
        <p className="line-clamp-2 text-xs leading-5 text-ink">{client.goals}</p>
      </div>

      <div className="mt-2 grid grid-cols-2 gap-1.5">
        <MiniFact icon={<CalendarDays size={12} />} label="Last" value={lastWorkout} />
        <MiniFact icon={<ClipboardList size={12} />} label="Plan" value={`${stats.sets} sets / ${stats.volumeKg}kg`} />
      </div>

      <div className="mt-2 min-w-0">
        <p className="truncate text-xs font-bold text-ink">{programVariantName(client, program)}</p>
        <div className="mt-1 flex flex-wrap gap-1">
          {exercises.map((exercise) => (
            <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-muted" key={exercise.id}>
              {exercise.exercise.name}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-2 grid grid-cols-2 gap-1.5">
        <a className="inline-flex min-h-8 items-center justify-center gap-1.5 rounded-md border border-line bg-white px-2 text-xs font-bold text-ink transition hover:bg-panel" href={routes.client(client.id)}>
          Profile
          <ExternalLink size={12} />
        </a>
        <a className="inline-flex min-h-8 items-center justify-center gap-1.5 rounded-md bg-ink px-2 text-xs font-bold text-white transition hover:bg-slate-800" href={routes.program(program.id)}>
          Plan
          <ExternalLink size={12} />
        </a>
      </div>
    </article>
  );
}

function MiniFact({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-white px-2 py-1.5">
      <p className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide text-muted">
        {icon}
        {label}
      </p>
      <p className="mt-0.5 truncate text-xs font-bold text-ink">{value}</p>
    </div>
  );
}

function focusClassName(focus: string | null) {
  const base = "rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide";
  if (focus === "Conditioning Circuit") return `${base} border-amber-200 bg-amber-50 text-warning`;
  if (focus === "Core Stability") return `${base} border-emerald-200 bg-emerald-50 text-success`;
  if (focus === "Strength Block") return `${base} border-blue-200 bg-blue-50 text-brand`;
  return `${base} border-line bg-panel text-muted`;
}
