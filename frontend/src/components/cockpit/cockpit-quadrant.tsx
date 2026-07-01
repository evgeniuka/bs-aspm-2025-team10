"use client";

import { AlertTriangle, Check, CheckCircle2, Play, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { CompleteSetPayload } from "@/lib/api";
import type { SessionParticipant } from "@/lib/types";
import { formatTimer } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

function restSecondsRemaining(participant: SessionParticipant, now: number) {
  if (participant.status !== "resting") return participant.rest_time_remaining;
  if (!participant.rest_ends_at) return participant.rest_time_remaining;
  // Anchor the countdown to the server's absolute end time so it survives remounts,
  // reconnects, and unrelated broadcasts instead of resetting to the full duration.
  // Treat a timezone-less timestamp (SQLite stores DateTime as naive) as UTC, so the
  // countdown is not skewed by the browser's local UTC offset.
  const raw = participant.rest_ends_at;
  const iso = /[zZ]|[+-]\d\d:?\d\d$/.test(raw) ? raw : `${raw}Z`;
  return Math.max(0, Math.round((new Date(iso).getTime() - now) / 1000));
}

export function CockpitQuadrant({
  participant,
  onCompleteSet,
  onStartNextSet,
  onUndoLastSet,
  disabled = false
}: {
  participant: SessionParticipant;
  onCompleteSet: (clientId: number, payload: Required<CompleteSetPayload>) => void;
  onStartNextSet: (clientId: number) => void;
  onUndoLastSet: (clientId: number) => void;
  disabled?: boolean;
}) {
  const [now, setNow] = useState(() => Date.now());
  const current = participant.program.exercises[participant.current_exercise_index];
  const [actualReps, setActualReps] = useState(() => String(current?.reps ?? 0));
  const [actualWeight, setActualWeight] = useState(() => String(current?.weight_kg ?? 0));
  const isComplete = participant.status === "completed" || !current;
  const completedSets = participant.sets_completed.length;
  const totalPlannedSets = useMemo(
    () => participant.program.exercises.reduce((sum, exercise) => sum + exercise.sets, 0),
    [participant.program.exercises]
  );
  const completedVolume = useMemo(
    () => participant.sets_completed.reduce((sum, set) => sum + set.volume_kg, 0),
    [participant.sets_completed]
  );
  const restTimer = restSecondsRemaining(participant, now);
  const progress = useMemo(() => {
    if (totalPlannedSets === 0) return 0;
    return Math.min(100, Math.round((completedSets / totalPlannedSets) * 100));
  }, [completedSets, totalPlannedSets]);

  useEffect(() => {
    if (participant.status !== "resting" || !participant.rest_ends_at) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [participant.status, participant.rest_ends_at]);

  function completeSet() {
    if (!current) return;
    onCompleteSet(participant.client_id, {
      program_exercise_id: current.id,
      exercise_id: current.exercise.id,
      set_number: participant.current_set,
      reps_completed: Math.max(0, Math.round(Number(actualReps) || 0)),
      weight_kg: Math.max(0, Number(actualWeight) || 0)
    });
  }

  return (
    <Card className={`flex min-h-[280px] flex-col justify-between overflow-hidden p-4 ${quadrantClassName(participant.status)}`} data-testid="cockpit-card">
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <ClientAvatar name={participant.client_name} size="lg" />
            <div className="min-w-0">
              <h3 className="truncate text-lg font-semibold text-ink">{participant.client_name}</h3>
              <p className="truncate text-sm text-muted">{participant.program.name}</p>
            </div>
          </div>
          <span className={statusClassName(participant.status)}>{participant.status}</span>
        </div>
        <div className="mt-5">
          <p className="field-label">Current exercise</p>
          <p className="mt-1 text-xl font-semibold text-ink">{current?.exercise.name ?? "Workout complete"}</p>
          {current && (
            <p className="mt-1 text-sm text-muted">
              Set {participant.current_set} of {current.sets} · {current.reps} reps · {current.weight_kg}kg
            </p>
          )}
          <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
            <MiniStat label="Sets" value={`${completedSets}/${totalPlannedSets}`} />
            <MiniStat label="Exercise" value={`${Math.min(participant.current_exercise_index + 1, participant.program.exercises.length)}/${participant.program.exercises.length}`} />
            <MiniStat label="Volume" value={`${completedVolume}kg`} />
          </div>
          {participant.today_check_in && (
            <div className="mt-3 rounded-lg border border-line bg-panel px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <p className="field-label">Today check-in</p>
                <span className={checkInStatusClass(participant.today_check_in.readiness_status)}>
                  {participant.today_check_in.readiness_status === "attention" && <AlertTriangle size={12} />}
                  {participant.today_check_in.readiness_status}
                </span>
              </div>
              <p className="mt-1 text-xs text-muted">
                Energy {participant.today_check_in.energy_level}/5 · Sleep {participant.today_check_in.sleep_quality}/5 · Soreness {participant.today_check_in.soreness_level}/5
              </p>
              {participant.today_check_in.pain_notes && (
                <p className="mt-1 line-clamp-2 text-xs font-medium text-ink">{participant.today_check_in.pain_notes}</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <div className="mb-1.5 flex justify-between text-xs text-muted">
            <span>Session progress</span>
            <span className="font-medium text-ink">{progress}%</span>
          </div>
          <div className="meter-track">
            <div className="meter-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {isComplete ? (
          <div className="flex items-center gap-3 rounded-lg border border-success-soft bg-success-soft p-3">
            <CheckCircle2 className="text-success" size={20} />
            <div>
              <p className="text-xs font-medium text-success">Saved</p>
              <p className="text-sm font-medium text-ink">Client history updated</p>
            </div>
          </div>
        ) : participant.status === "resting" ? (
          <div className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-lg bg-warning-soft p-3">
            <div>
              <p className="field-label text-warning">Rest timer</p>
              <p className="text-2xl font-semibold text-warning">{formatTimer(restTimer)}</p>
            </div>
            <Button disabled={disabled} variant="secondary" onClick={() => onStartNextSet(participant.client_id)}>
              <Play size={16} />
              Start
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {current && (
              <div className="grid grid-cols-2 gap-2">
                <label className="block">
                  <span className="field-label">Actual reps</span>
                  <input
                    aria-label={`Actual reps for ${participant.client_name}`}
                    className="field-control"
                    inputMode="numeric"
                    min={0}
                    step={1}
                    type="number"
                    value={actualReps}
                    onChange={(event) => setActualReps(event.target.value)}
                  />
                </label>
                <label className="block">
                  <span className="field-label">Actual kg</span>
                  <input
                    aria-label={`Actual weight for ${participant.client_name}`}
                    className="field-control"
                    inputMode="decimal"
                    min={0}
                    step={0.5}
                    type="number"
                    value={actualWeight}
                    onChange={(event) => setActualWeight(event.target.value)}
                  />
                </label>
              </div>
            )}
            <Button className="w-full" disabled={disabled || participant.status === "completed" || !current} onClick={completeSet}>
              <Check size={16} />
              Complete set
            </Button>
          </div>
        )}
        {!isComplete && completedSets > 0 && (
          <button
            className="inline-flex min-h-9 w-full items-center justify-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-sm font-medium text-muted transition hover:bg-panel hover:text-ink disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            type="button"
            onClick={() => onUndoLastSet(participant.client_id)}
          >
            <RotateCcw size={15} />
            Undo last set
          </button>
        )}
      </div>
    </Card>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-panel px-2.5 py-1.5">
      <p className="text-[11px] text-muted">{label}</p>
      <p className="mt-0.5 font-semibold text-ink">{value}</p>
    </div>
  );
}

function quadrantClassName(status: SessionParticipant["status"]) {
  if (status === "working") return "border-brand-soft bg-brand-soft/40";
  if (status === "resting") return "border-warning-soft bg-warning-soft/50";
  if (status === "completed") return "border-success-soft bg-success-soft/50";
  return "";
}

function statusClassName(status: SessionParticipant["status"]) {
  const base = "rounded-full px-2.5 py-0.5 text-xs font-medium capitalize";
  if (status === "working") return `${base} bg-brand-soft text-brand`;
  if (status === "resting") return `${base} bg-warning-soft text-warning`;
  if (status === "completed") return `${base} bg-success-soft text-success`;
  return `${base} bg-panel text-muted`;
}

function checkInStatusClass(status: NonNullable<SessionParticipant["today_check_in"]>["readiness_status"]) {
  const base = "inline-flex min-h-6 items-center gap-1 rounded-full px-2 text-[11px] font-medium capitalize";
  if (status === "attention") return `${base} bg-danger-soft text-danger`;
  if (status === "caution") return `${base} bg-warning-soft text-warning`;
  return `${base} bg-success-soft text-success`;
}
