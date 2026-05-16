"use client";

import { clsx } from "clsx";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import { routes } from "@/lib/routes";
import type { Exercise, ProgramFocus } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export function ProgramBuilder({ variant = "default" }: { variant?: "default" | "rail" }) {
  const queryClient = useQueryClient();
  const { data: clients = [] } = useQuery({ queryKey: ["clients"], queryFn: api.clients });
  const { data: exercises = [] } = useQuery({ queryKey: ["exercises"], queryFn: api.exercises });
  const [clientId, setClientId] = useState<number | "">("");
  const [programFocus, setProgramFocus] = useState<ProgramFocus>("Strength Block");
  const [programName, setProgramName] = useState("Strength Block");
  const selectedExercises = useMemo(() => pickDefaults(exercises, programFocus), [exercises, programFocus]);
  const isRail = variant === "rail";

  const create = useMutation({
    mutationFn: () =>
      api.createProgram({
        client_id: Number(clientId),
        name: programName,
        focus: programFocus,
        notes: "Built from the portfolio demo program builder.",
        exercises: selectedExercises.map((exercise, index) => ({
          exercise_id: exercise.id,
          sets: 3,
          reps: 8 + index * 2,
          weight_kg: 20 + index * 5,
          rest_seconds: 45 + index * 15
        }))
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["programs"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["trainer-analytics"] });
    }
  });

  const builderControls = (
    <>
      <div className={clsx("grid gap-3", !isRail && "sm:grid-cols-2")}>
        <label className="block">
          <span className="field-label">Client</span>
          <select
            className="field-control"
            value={clientId}
            onChange={(event) => setClientId(Number(event.target.value))}
          >
            <option value="">Select client</option>
            {clients.map((client) => (
              <option key={client.id} value={client.id}>
                {client.name}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="field-label">Workout focus</span>
          <select
            className="field-control"
            value={programFocus}
            onChange={(event) => {
              const focus = event.target.value as ProgramFocus;
              setProgramFocus(focus);
              setProgramName(focus);
            }}
          >
            <option value="Strength Block">Strength Block</option>
            <option value="Conditioning Circuit">Conditioning Circuit</option>
            <option value="Core Stability">Core Stability</option>
          </select>
        </label>
        <label className="block">
          <span className="field-label">Program name</span>
          <input
            className="field-control"
            value={programName}
            onChange={(event) => setProgramName(event.target.value)}
          />
        </label>
      </div>
      <div className="overflow-hidden rounded-md border border-line">
        {selectedExercises.slice(0, isRail ? 4 : selectedExercises.length).map((exercise, index) => (
          <div className="grid grid-cols-[36px_1fr_88px] items-center gap-3 border-b border-line px-3 py-2.5 last:border-0" key={exercise.id}>
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-panel text-xs font-bold text-muted">{index + 1}</span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-ink">{exercise.name}</span>
              <span className="text-xs text-muted">{exercise.category} - {exercise.equipment}</span>
            </span>
            <span className="text-right text-xs font-semibold text-muted">3 sets</span>
          </div>
        ))}
      </div>
      <div className={clsx("flex flex-wrap items-center gap-2", isRail && "flex-col items-stretch")}>
        <Button className={isRail ? "w-full" : undefined} disabled={!clientId || selectedExercises.length < 3 || create.isPending} onClick={() => create.mutate()}>
          <Plus size={16} />
          {create.isPending ? "Creating..." : "Create program"}
        </Button>
        {create.data && (
          <a
            className={clsx(
              "inline-flex min-h-10 items-center justify-center rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-panel",
              isRail && "w-full"
            )}
            href={routes.program(create.data.id)}
          >
            Edit created program
          </a>
        )}
      </div>
    </>
  );

  return (
    <Card className={clsx("overflow-hidden", isRail && "bg-white/90")}>
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-ink">{isRail ? "Build workout" : "Program builder"}</h2>
            <p className="text-xs text-muted">{isRail ? "Create a plan without leaving setup" : "Create a reusable block from the exercise library"}</p>
          </div>
          <span className="status-pill">{selectedExercises.length} exercises</span>
        </div>
      </CardHeader>
      <CardBody className={clsx("space-y-4", isRail && "p-3")}>
        {isRail ? (
          <details>
            <summary className="cursor-pointer rounded-md border border-line bg-white px-3 py-2 text-sm font-bold text-ink transition hover:bg-panel">
              Open quick builder
            </summary>
            <div className="mt-3 space-y-4">{builderControls}</div>
          </details>
        ) : (
          builderControls
        )}
      </CardBody>
    </Card>
  );
}

const WORKOUT_DEFAULTS: Record<ProgramFocus, string[]> = {
  "Strength Block": ["Goblet Squat", "Dumbbell Bench Press", "Romanian Deadlift", "TRX Row"],
  "Conditioning Circuit": ["Bike Sprint", "Walking Lunge", "Farmer Carry", "Plank Hold"],
  "Core Stability": ["Dead Bug", "Pallof Press", "Step Up", "Tempo Split Squat"]
};

function pickDefaults(exercises: Exercise[], focus: ProgramFocus) {
  const byName = new Map(exercises.map((exercise) => [exercise.name, exercise]));
  const preferred = WORKOUT_DEFAULTS[focus].map((name) => byName.get(name)).filter((exercise): exercise is Exercise => Boolean(exercise));
  return preferred.length >= 3 ? preferred : exercises.slice(0, 4);
}
