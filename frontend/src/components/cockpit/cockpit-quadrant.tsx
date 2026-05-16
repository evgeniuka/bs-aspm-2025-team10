"use client";

import { AlertTriangle, Check, CheckCircle2, Play, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { CompleteSetPayload } from "@/lib/api";
import type { SessionParticipant } from "@/lib/types";
import { formatTimer } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

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
  const [displayedRest, setDisplayedRest] = useState(() => participant.rest_time_remaining);
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
  const restTimer =
    participant.status === "resting"
      ? displayedRest
      : participant.rest_time_remaining;
  const progress = useMemo(() => {
    if (totalPlannedSets === 0) return 0;
    return Math.min(100, Math.round((completedSets / totalPlannedSets) * 100));
  }, [completedSets, totalPlannedSets]);

  useEffect(() => {
    if (participant.status !== "resting") return;
    const restStartedAt = Date.now();
    const id = window.setInterval(() => {
      setDisplayedRest(Math.max(0, participant.rest_time_remaining - Math.floor((Date.now() - restStartedAt) / 1000)));
    }, 1000);
    return () => window.clearInterval(id);
  }, [participant.rest_time_remaining, participant.status]);

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
              <h3 className="truncate text-xl font-bold text-ink">{participant.client_name}</h3>
              <p className="truncate text-sm text-muted">{participant.program.name}</p>
            </div>
          </div>
          <span className={statusClassName(participant.status)}>{participant.status}</span>
        </div>
        <div className="mt-5">
          <p className="text-xs font-semibold uppercase text-muted">Current exercise</p>
          <p className="mt-1 text-2xl font-bold text-ink">{current?.exercise.name ?? "Workout complete"}</p>
          {current && (
            <p className="mt-1 text-sm text-muted">
              Set {participant.current_set} of {current.sets} - {current.reps} reps - {current.weight_kg}kg
            </p>
          )}
          <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
            <MiniStat label="Sets" value={`${completedSets}/${totalPlannedSets}`} />
            <MiniStat label="Exercise" value={`${Math.min(participant.current_exercise_index + 1, participant.program.exercises.length)}/${participant.program.exercises.length}`} />
            <MiniStat label="Volume" value={`${completedVolume}kg`} />
          </div>
          {participant.today_check_in && (
            <div className="mt-3 rounded-md border border-line bg-white/75 px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <p className="field-label">Today check-in</p>
                <span className={checkInStatusClass(participant.today_check_in.readiness_status)}>
                  {participant.today_check_in.readiness_status === "attention" && <AlertTriangle size={12} />}
                  {participant.today_check_in.readiness_status}
                </span>
              </div>
              <p className="mt-1 text-xs font-semibold text-muted">
                Energy {participant.today_check_in.energy_level}/5 - Sleep {participant.today_check_in.sleep_quality}/5 - Soreness {participant.today_check_in.soreness_level}/5
              </p>
              {participant.today_check_in.pain_notes && (
                <p className="mt-1 line-clamp-2 text-xs font-semibold text-ink">{participant.today_check_in.pain_notes}</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <div className="mb-1 flex justify-between text-xs font-semibold text-muted">
            <span>Session progress</span>
            <span>{progress}%</span>
          </div>
          <div className="meter-track">
            <div className="meter-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {isComplete ? (
          <div className="flex items-center gap-3 rounded-md border border-emerald-200 bg-emerald-50 p-3">
            <CheckCircle2 className="text-success" size={22} />
            <div>
              <p className="text-xs font-semibold uppercase text-success">Saved</p>
              <p className="text-sm font-semibold text-ink">Client history updated</p>
            </div>
          </div>
        ) : participant.status === "resting" ? (
          <div className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-md bg-amber-50 p-3">
            <div>
              <p className="text-xs font-semibold uppercase text-warning">Rest timer</p>
              <p className="text-2xl font-bold text-warning">{formatTimer(restTimer)}</p>
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
            className="inline-flex min-h-9 w-full items-center justify-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-muted transition hover:bg-panel hover:text-ink disabled:cursor-not-allowed disabled:opacity-50"
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
    <div className="rounded-md border border-line bg-white/80 px-2 py-1.5">
      <p className="text-[10px] font-bold uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-0.5 font-bold text-ink">{value}</p>
    </div>
  );
}

function quadrantClassName(status: SessionParticipant["status"]) {
  if (status === "working") return "border-blue-200 bg-blue-50/40";
  if (status === "resting") return "border-amber-200 bg-amber-50/45";
  if (status === "completed") return "border-emerald-200 bg-emerald-50/45";
  return "bg-white/90";
}

function statusClassName(status: SessionParticipant["status"]) {
  const base = "rounded-full border px-3 py-1 text-xs font-bold uppercase";
  if (status === "working") return `${base} border-blue-200 bg-blue-50 text-brand`;
  if (status === "resting") return `${base} border-amber-200 bg-amber-50 text-warning`;
  if (status === "completed") return `${base} border-emerald-200 bg-emerald-50 text-success`;
  return `${base} border-line bg-panel text-muted`;
}

function checkInStatusClass(status: NonNullable<SessionParticipant["today_check_in"]>["readiness_status"]) {
  const base = "inline-flex min-h-6 items-center gap-1 rounded-full border px-2 text-[10px] font-bold uppercase";
  if (status === "attention") return `${base} border-red-200 bg-red-50 text-danger`;
  if (status === "caution") return `${base} border-amber-200 bg-amber-50 text-warning`;
  return `${base} border-emerald-200 bg-emerald-50 text-success`;
}
