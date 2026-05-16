"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowDown, ArrowLeft, ArrowUp, Dumbbell, Pencil, Plus, Save, Search, Trash2 } from "lucide-react";
import type { Dispatch, ReactNode, SetStateAction } from "react";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { ClientDetail, Exercise, Program, ProgramFocus } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

type ProgramRow = {
  exercise_id: number;
  sets: number;
  reps: number;
  weight_kg: number;
  rest_seconds: number;
  notes: string | null;
};

type SetRows = Dispatch<SetStateAction<ProgramRow[]>>;

export function ProgramEditor({ programId }: { programId: number }) {
  const programQuery = useQuery({ queryKey: ["program", programId], queryFn: () => api.program(programId), retry: false });
  const exercisesQuery = useQuery({ queryKey: ["exercises"], queryFn: api.exercises, retry: false });
  const program = programQuery.data;
  const clientId = program?.client_id;
  const clientDetailQuery = useQuery({
    queryKey: ["client-detail", clientId],
    queryFn: () => api.clientDetail(clientId as number),
    enabled: Boolean(clientId),
    retry: false
  });

  if (programQuery.isLoading) {
    return <div className="page-wrap text-sm text-muted">Loading program...</div>;
  }

  if (programQuery.error || !program) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <Card className="max-w-md">
          <CardBody className="space-y-4">
            <p className="text-sm text-muted">Could not load this program.</p>
            <a className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white" href={routes.dashboard}>
              Back to dashboard
            </a>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <ProgramEditorForm
      clientDetail={clientDetailQuery.data}
      clientDetailError={clientDetailQuery.error ? getErrorMessage(clientDetailQuery.error) : null}
      exercises={exercisesQuery.data ?? []}
      exercisesError={exercisesQuery.error ? getErrorMessage(exercisesQuery.error) : null}
      isClientDetailLoading={clientDetailQuery.isLoading}
      isExercisesLoading={exercisesQuery.isLoading}
      key={program.id}
      program={program}
    />
  );
}

function ProgramEditorForm({
  clientDetail,
  clientDetailError,
  exercises,
  exercisesError,
  isClientDetailLoading,
  isExercisesLoading,
  program
}: {
  clientDetail: ClientDetail | undefined;
  clientDetailError: string | null;
  exercises: Exercise[];
  exercisesError: string | null;
  isClientDetailLoading: boolean;
  isExercisesLoading: boolean;
  program: Program;
}) {
  const queryClient = useQueryClient();
  const [name, setName] = useState(program.name);
  const [focus, setFocus] = useState<ProgramFocus>(program.focus ?? "Strength Block");
  const [notes, setNotes] = useState(programNotesForEditor(program.notes));
  const [rows, setRows] = useState<ProgramRow[]>(() => program.exercises.map(programExerciseToRow));
  const [isAddingExercise, setIsAddingExercise] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const exerciseLibrary = exercises.length > 0 ? exercises : program.exercises.map((item) => item.exercise);
  const exerciseById = useMemo(() => new Map(exerciseLibrary.map((exercise) => [exercise.id, exercise])), [exerciseLibrary]);
  const originalSnapshot = useMemo(() => programSnapshot(program.name, program.focus, programNotesForEditor(program.notes), program.exercises.map(programExerciseToRow)), [program]);
  const currentSnapshot = useMemo(() => programSnapshot(name, focus, notes, rows), [focus, name, notes, rows]);
  const isDirty = currentSnapshot !== originalSnapshot;
  const update = useMutation({
    mutationFn: () =>
      api.updateProgram(program.id, {
        name: name.trim(),
        focus,
        notes: notes.trim() || null,
        exercises: normalizedRows(rows)
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["program", program.id], updated);
      void queryClient.invalidateQueries({ queryKey: ["programs"] });
      void queryClient.invalidateQueries({ queryKey: ["client-detail", updated.client_id] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    }
  });
  const startSession = useMutation({
    mutationFn: () => api.startSession({ client_ids: [program.client_id], program_ids: [program.id] }),
    onSuccess: (data) => {
      window.location.assign(routes.session(data.session_id));
    }
  });
  const validationMessages = getValidationMessages(name, rows);
  const canSave = validationMessages.length === 0;
  const clientName = clientDetail?.client.name ?? `Client #${program.client_id}`;
  const saveState = getSaveState({ canSave, isDirty, isPending: update.isPending, isSuccess: update.isSuccess, error: update.error });
  const totalSets = rows.reduce((sum, row) => sum + row.sets, 0);
  const plannedVolume = rows.reduce((sum, row) => sum + row.sets * row.reps * row.weight_kg, 0);

  function handleAddExercise(exercise: Exercise) {
    setRows((currentRows) => [...currentRows, exerciseToDefaultRow(exercise)]);
    setIsAddingExercise(false);
  }

  function discardChanges() {
    setName(program.name);
    setFocus(program.focus ?? "Strength Block");
    setNotes(programNotesForEditor(program.notes));
    setRows(program.exercises.map(programExerciseToRow));
    setIsAddingExercise(false);
    update.reset();
    setIsEditing(false);
  }

  return (
    <div className="page-wrap">
      <header className="page-titlebar">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <a className="status-pill hover:bg-panel" href={routes.client(program.client_id)}>
                <ArrowLeft size={13} />
                {clientName}
              </a>
              <span className="status-pill">{rows.length} exercises</span>
              {isEditing ? <span className={`status-pill ${saveState.tone}`}>{saveState.label}</span> : <span className="status-pill">{totalSets} sets</span>}
            </div>
            <p className="mt-3 text-xs font-bold uppercase tracking-wide text-muted">{isEditing ? "Edit plan" : "Today's plan"}</p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight text-ink">{name || "Untitled program"}</h1>
            <p className="mt-1 max-w-3xl text-sm text-muted">
              {isEditing ? "Adjust the plan, save changes, then return to a simple session-ready view." : "Scan the plan and start when the client is ready."}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {isEditing ? (
              <>
                <Button variant="secondary" onClick={discardChanges}>
                  {isDirty ? "Discard" : "View plan"}
                </Button>
                <Button disabled={!canSave || !isDirty || update.isPending} onClick={() => update.mutate()}>
                  <Save size={16} />
                  {update.isPending ? "Saving..." : "Save program"}
                </Button>
              </>
            ) : (
              <>
                <Button disabled={!canSave || startSession.isPending || update.isPending} onClick={() => startSession.mutate()}>
                  <Dumbbell size={16} />
                  {startSession.isPending ? "Opening..." : "Start session"}
                </Button>
                <Button variant="secondary" onClick={() => setIsEditing(true)}>
                  <Pencil size={16} />
                  Edit plan
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {isEditing ? (
        <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-4">
            <ClientContextPanel
              clientDetail={clientDetail}
              clientDetailError={clientDetailError}
              isLoading={isClientDetailLoading}
              plannedSets={totalSets}
              plannedVolume={plannedVolume}
            />

            <Card>
              <CardHeader className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-bold text-ink">Training plan</h2>
                  <p className="text-xs text-muted">Order exercises, tune loading, and keep cues visible for the session.</p>
                </div>
                <Button disabled={isExercisesLoading || exercises.length === 0 || rows.length >= 20} size="sm" variant="secondary" onClick={() => setIsAddingExercise((value) => !value)}>
                  <Plus size={14} />
                  Add exercise
                </Button>
              </CardHeader>
              <CardBody className="space-y-3">
                {exercisesError && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{exercisesError}</p>}
                {isAddingExercise && (
                  <AddExercisePanel exercises={exercises} rows={rows} onAdd={handleAddExercise} onClose={() => setIsAddingExercise(false)} />
                )}
                {isExercisesLoading ? (
                  <p className="text-sm text-muted">Loading exercise library...</p>
                ) : (
                  <ExerciseRows exercises={exercises} exerciseById={exerciseById} rows={rows} setRows={setRows} />
                )}
              </CardBody>
            </Card>
          </div>

          <aside className="space-y-4">
            <Card>
              <CardHeader>
                <h2 className="text-base font-bold text-ink">Program details</h2>
              </CardHeader>
              <CardBody className="space-y-4">
                <label className="block">
                  <span className="field-label">Program name</span>
                  <input aria-label="Program name" className="field-control" value={name} onChange={(event) => setName(event.target.value)} />
                </label>
                <label className="block">
                  <span className="field-label">Workout focus</span>
                  <select
                    aria-label="Workout focus"
                    className="field-control"
                    value={focus}
                    onChange={(event) => setFocus(event.target.value as ProgramFocus)}
                  >
                    <option value="Strength Block">Strength Block</option>
                    <option value="Conditioning Circuit">Conditioning Circuit</option>
                    <option value="Core Stability">Core Stability</option>
                  </select>
                </label>
                <label className="block">
                  <span className="field-label">Coach notes</span>
                  <textarea
                    aria-label="Coach notes"
                    className="field-control min-h-32 resize-y"
                    placeholder="Session intent, constraints, progression target"
                    value={notes}
                    onChange={(event) => setNotes(event.target.value)}
                  />
                </label>
                <div className="rounded-md bg-panel p-3 text-sm">
                  <div className="flex items-center justify-between gap-3 border-b border-line pb-2">
                    <span className="text-muted">Planned sets</span>
                    <span className="font-bold text-ink">{totalSets}</span>
                  </div>
                  <div className="flex items-center justify-between gap-3 pt-2">
                    <span className="text-muted">Planned volume</span>
                    <span className="font-bold text-ink">{plannedVolume}kg</span>
                  </div>
                </div>
                {validationMessages.length > 0 && (
                  <div className="rounded-md bg-amber-50 p-3 text-sm text-amber-900">
                    <p className="font-bold">Before saving</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {validationMessages.map((message) => (
                        <li key={message}>{message}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {update.error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{getErrorMessage(update.error)}</p>}
                {startSession.error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{getErrorMessage(startSession.error)}</p>}
                {!isDirty && update.isSuccess && <p className="rounded-md bg-emerald-50 p-3 text-sm font-semibold text-success">Program saved.</p>}
              </CardBody>
            </Card>
          </aside>
        </section>
      ) : (
        <section className="space-y-4">
          <QuickClientContext clientDetail={clientDetail} clientDetailError={clientDetailError} isLoading={isClientDetailLoading} />
          {startSession.error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{getErrorMessage(startSession.error)}</p>}
          <Card>
            <CardHeader className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-bold text-ink">Session plan</h2>
                <p className="text-xs text-muted">{totalSets} planned sets, {plannedVolume}kg planned volume</p>
              </div>
              <Button size="sm" variant="secondary" onClick={() => setIsEditing(true)}>
                <Pencil size={14} />
                Edit
              </Button>
            </CardHeader>
            <CardBody>
              <PlanPreviewRows exerciseById={exerciseById} rows={rows} />
            </CardBody>
          </Card>
        </section>
      )}
    </div>
  );
}

function ClientContextPanel({
  clientDetail,
  clientDetailError,
  isLoading,
  plannedSets,
  plannedVolume
}: {
  clientDetail: ClientDetail | undefined;
  clientDetailError: string | null;
  isLoading: boolean;
  plannedSets: number;
  plannedVolume: number;
}) {
  if (isLoading) {
    return (
      <Card>
        <CardBody className="text-sm text-muted">Loading client context...</CardBody>
      </Card>
    );
  }

  if (clientDetailError || !clientDetail) {
    return (
      <Card>
        <CardBody className="text-sm text-muted">Client context is unavailable. You can still edit and save this program.</CardBody>
      </Card>
    );
  }

  const { analytics, client, recent_sessions: recentSessions } = clientDetail;
  const lastSession = recentSessions[0];
  const completionRate = lastSession?.planned_sets ? Math.round((lastSession.sets_completed / lastSession.planned_sets) * 100) : 0;
  const nextFocus = lastSession?.next_focus || "Set after this session";
  const lastNote = lastSession?.coach_notes || "No recent coach note";

  return (
    <Card>
      <CardHeader className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-ink">Client context</h2>
          <p className="text-xs text-muted">{client.goals}</p>
        </div>
        <span className="status-pill">{client.fitness_level}</span>
      </CardHeader>
      <CardBody className="grid gap-3 md:grid-cols-4">
        <ContextMetric label="Last workout" value={client.last_workout_date ? formatDate(client.last_workout_date) : "No workout"} />
        <ContextMetric label="Last completion" value={lastSession ? `${completionRate}%` : "No history"} />
        <ContextMetric label="Program target" value={`${plannedSets} sets / ${plannedVolume}kg`} />
        <ContextMetric label="History volume" value={`${analytics.total_volume_kg}kg`} />
        <div className="rounded-md border border-line bg-panel p-3 md:col-span-2">
          <p className="field-label">Next focus</p>
          <p className="mt-1 text-sm font-semibold text-ink">{nextFocus}</p>
        </div>
        <div className="rounded-md border border-line bg-panel p-3 md:col-span-2">
          <p className="field-label">Last coach note</p>
          <p className="mt-1 text-sm text-ink">{lastNote}</p>
        </div>
        {lastSession && (
          <a className="rounded-md border border-line px-3 py-2 text-sm font-semibold text-ink transition hover:bg-panel md:col-span-4" href={routes.sessionSummary(lastSession.session_id)}>
            Last session: {lastSession.program_name} - {lastSession.sets_completed}/{lastSession.planned_sets} sets, {formatDuration(lastSession.duration_minutes)}
          </a>
        )}
      </CardBody>
    </Card>
  );
}

function QuickClientContext({
  clientDetail,
  clientDetailError,
  isLoading
}: {
  clientDetail: ClientDetail | undefined;
  clientDetailError: string | null;
  isLoading: boolean;
}) {
  if (isLoading) {
    return <p className="text-sm text-muted">Loading client context...</p>;
  }

  if (clientDetailError || !clientDetail) {
    return <p className="rounded-md border border-line bg-white p-3 text-sm text-muted">Client context is unavailable. The plan is still ready to start.</p>;
  }

  const { client, recent_sessions: recentSessions } = clientDetail;
  const lastSession = recentSessions[0];
  const nextFocus = lastSession?.next_focus || "Set after this session";

  return (
    <div className="grid gap-3 rounded-lg border border-line bg-white p-3 shadow-panel md:grid-cols-[minmax(0,1fr)_auto_auto]">
      <div className="min-w-0">
        <p className="field-label">Client</p>
        <p className="truncate text-sm font-bold text-ink">{client.name}</p>
        <p className="mt-1 truncate text-xs text-muted">{client.goals}</p>
      </div>
      <div className="rounded-md bg-panel p-3">
        <p className="field-label">Last workout</p>
        <p className="mt-1 text-sm font-bold text-ink">{client.last_workout_date ? formatDate(client.last_workout_date) : "No workout"}</p>
      </div>
      <div className="rounded-md bg-panel p-3">
        <p className="field-label">Next focus</p>
        <p className="mt-1 text-sm font-bold text-ink">{nextFocus}</p>
      </div>
    </div>
  );
}

function ContextMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-white p-3">
      <p className="field-label">{label}</p>
      <p className="mt-1 text-sm font-bold text-ink">{value}</p>
    </div>
  );
}

function PlanPreviewRows({ exerciseById, rows }: { exerciseById: Map<number, Exercise>; rows: ProgramRow[] }) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {rows.map((row, index) => {
        const exercise = exerciseById.get(row.exercise_id);
        const exerciseName = exercise?.name ?? `Exercise ${index + 1}`;
        return (
          <article className="rounded-md border border-line bg-white p-3" key={`${row.exercise_id}-${index}`}>
            <div className="flex items-start gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-panel text-xs font-bold text-muted">{index + 1}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-bold text-ink">{exerciseName}</p>
                <p className="text-xs text-muted">{exerciseMeta(exercise)}</p>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-4 gap-2 text-center text-sm">
              <PlanChip label="Sets" value={String(row.sets)} />
              <PlanChip label="Reps" value={String(row.reps)} />
              <PlanChip label="Kg" value={String(row.weight_kg)} />
              <PlanChip label="Rest" value={`${row.rest_seconds}s`} />
            </div>
            {row.notes?.trim() && (
              <p className="mt-3 rounded-md bg-panel px-3 py-2 text-xs text-muted">{row.notes}</p>
            )}
          </article>
        );
      })}
    </div>
  );
}

function PlanChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-panel px-2 py-2">
      <p className="text-[10px] font-bold uppercase text-muted">{label}</p>
      <p className="mt-1 font-bold text-ink">{value}</p>
    </div>
  );
}

function AddExercisePanel({
  exercises,
  rows,
  onAdd,
  onClose
}: {
  exercises: Exercise[];
  rows: ProgramRow[];
  onAdd: (exercise: Exercise) => void;
  onClose: () => void;
}) {
  const [query, setQuery] = useState("");
  const [duplicateExerciseId, setDuplicateExerciseId] = useState<number | null>(null);
  const normalizedQuery = query.trim().toLowerCase();
  const filtered = normalizedQuery
    ? exercises.filter((exercise) =>
        [exercise.name, exercise.category, exercise.equipment, exercise.difficulty].some((value) => value.toLowerCase().includes(normalizedQuery))
      )
    : exercises;

  function handleAdd(exercise: Exercise) {
    const isDuplicate = rows.some((row) => row.exercise_id === exercise.id);
    if (isDuplicate && duplicateExerciseId !== exercise.id) {
      setDuplicateExerciseId(exercise.id);
      return;
    }
    onAdd(exercise);
    setDuplicateExerciseId(null);
  }

  return (
    <div className="rounded-md border border-brand/25 bg-blue-50/60 p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-sm font-bold text-ink">Add exercise</p>
          <p className="text-xs text-muted">Search by name, category, equipment, or difficulty.</p>
        </div>
        <button className="text-xs font-bold uppercase text-muted hover:text-ink" type="button" onClick={onClose}>
          Close
        </button>
      </div>
      <label className="relative mt-3 block">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={15} />
        <input
          aria-label="Search exercise library"
          className="field-control pl-9"
          placeholder="Search exercise library"
          type="search"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setDuplicateExerciseId(null);
          }}
        />
      </label>
      <div className="mt-3 grid max-h-72 gap-2 overflow-y-auto md:grid-cols-2">
        {filtered.map((exercise) => {
          const isDuplicate = rows.some((row) => row.exercise_id === exercise.id);
          const needsConfirmation = duplicateExerciseId === exercise.id;
          return (
            <div className="rounded-md border border-line bg-white p-3" key={exercise.id}>
              <p className="text-sm font-bold text-ink">{exercise.name}</p>
              <p className="mt-1 text-xs text-muted">
                {exercise.category} - {exercise.equipment} - {exercise.difficulty}
              </p>
              <button
                aria-label={`${needsConfirmation ? "Confirm duplicate" : "Add"} ${exercise.name}`}
                className="mt-3 inline-flex min-h-9 items-center justify-center rounded-md bg-brand px-3 text-xs font-bold uppercase text-white transition hover:bg-blue-700"
                type="button"
                onClick={() => handleAdd(exercise)}
              >
                {needsConfirmation ? "Confirm duplicate" : isDuplicate ? "Add duplicate" : "Add"}
              </button>
            </div>
          );
        })}
        {filtered.length === 0 && <p className="text-sm text-muted">No exercises match this search.</p>}
      </div>
      {duplicateExerciseId && <p className="mt-2 text-xs font-semibold text-amber-900">This exercise is already in the plan. Click confirm if you want it twice.</p>}
    </div>
  );
}

function ExerciseRows({
  exerciseById,
  exercises,
  rows,
  setRows
}: {
  exerciseById: Map<number, Exercise>;
  exercises: Exercise[];
  rows: ProgramRow[];
  setRows: SetRows;
}) {
  if (rows.length === 0) {
    return <p className="rounded-md border border-dashed border-line bg-panel p-4 text-sm text-muted">Add at least three exercises to build a program.</p>;
  }

  return (
    <>
      <div className="hidden lg:block">
        <div className="grid grid-cols-[32px_minmax(120px,1fr)_54px_54px_68px_68px_116px] gap-1.5 border-b border-line bg-panel px-3 py-2 text-[11px] font-bold uppercase tracking-wide text-muted">
          <span>#</span>
          <span>Exercise</span>
          <span className="text-right">Sets</span>
          <span className="text-right">Reps</span>
          <span className="text-right">Weight</span>
          <span className="text-right">Rest</span>
          <span className="text-right">Actions</span>
        </div>
        <div className="divide-y divide-line">
          {rows.map((row, index) => {
            const exercise = exerciseById.get(row.exercise_id);
            const exerciseName = exercise?.name ?? `Exercise ${index + 1}`;
            return (
              <div className="px-3 py-3" key={`${row.exercise_id}-${index}`}>
                <div className="grid grid-cols-[32px_minmax(120px,1fr)_54px_54px_68px_68px_116px] items-center gap-1.5">
                  <span className="flex h-8 w-8 items-center justify-center rounded-md bg-panel text-xs font-bold text-muted">{index + 1}</span>
                  <select
                    aria-label={`Exercise row ${index + 1}`}
                    className="min-w-0 rounded-md border border-line bg-white px-2 py-2 text-sm text-ink"
                    value={row.exercise_id}
                    onChange={(event) => updateRow(index, { exercise_id: Number(event.target.value) }, setRows)}
                  >
                    {exercises.map((exerciseItem) => (
                      <option key={exerciseItem.id} value={exerciseItem.id}>
                        {exerciseItem.name}
                      </option>
                    ))}
                  </select>
                  <NumberCell label={`Sets for ${exerciseName}`} min={1} value={row.sets} onChange={(value) => updateRow(index, { sets: value }, setRows)} />
                  <NumberCell label={`Reps for ${exerciseName}`} min={1} value={row.reps} onChange={(value) => updateRow(index, { reps: value }, setRows)} />
                  <NumberCell label={`Weight for ${exerciseName}`} min={0} value={row.weight_kg} onChange={(value) => updateRow(index, { weight_kg: value }, setRows)} />
                  <NumberCell label={`Rest for ${exerciseName}`} min={0} value={row.rest_seconds} onChange={(value) => updateRow(index, { rest_seconds: value }, setRows)} />
                  <RowActions exerciseName={exerciseName} index={index} rows={rows} setRows={setRows} />
                </div>
                <div className="mt-2 grid grid-cols-[36px_minmax(0,1fr)] gap-2">
                  <span />
                  <label className="block">
                    <span className="sr-only">Coach cue for {exerciseName}</span>
                    <textarea
                      aria-label={`Coach cue for ${exerciseName}`}
                      className="field-control min-h-12 resize-y py-1.5 text-xs"
                      placeholder={`${exerciseMeta(exercise)} - add cue or modification`}
                      value={row.notes ?? ""}
                      onChange={(event) => updateRow(index, { notes: event.target.value }, setRows)}
                    />
                  </label>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="space-y-3 lg:hidden">
        {rows.map((row, index) => {
          const exercise = exerciseById.get(row.exercise_id);
          const exerciseName = exercise?.name ?? `Exercise ${index + 1}`;
          return (
            <div className="rounded-md border border-line bg-white p-3" key={`${row.exercise_id}-${index}`}>
              <div className="mb-3 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <span className="mb-2 flex h-8 w-8 items-center justify-center rounded-md bg-panel text-xs font-bold text-muted">{index + 1}</span>
                  <p className="text-sm font-bold text-ink">{exerciseName}</p>
                  <p className="text-xs text-muted">{exerciseMeta(exercise)}</p>
                </div>
                <RowActions exerciseName={exerciseName} index={index} rows={rows} setRows={setRows} />
              </div>
              <label className="block">
                <span className="field-label">Exercise</span>
                <select
                  aria-label={`Exercise row ${index + 1}`}
                  className="field-control"
                  value={row.exercise_id}
                  onChange={(event) => updateRow(index, { exercise_id: Number(event.target.value) }, setRows)}
                >
                  {exercises.map((exerciseItem) => (
                    <option key={exerciseItem.id} value={exerciseItem.id}>
                      {exerciseItem.name}
                    </option>
                  ))}
                </select>
              </label>
              <div className="mt-3 grid grid-cols-2 gap-2">
                <NumberField label={`Sets for ${exerciseName}`} shortLabel="Sets" min={1} value={row.sets} onChange={(value) => updateRow(index, { sets: value }, setRows)} />
                <NumberField label={`Reps for ${exerciseName}`} shortLabel="Reps" min={1} value={row.reps} onChange={(value) => updateRow(index, { reps: value }, setRows)} />
                <NumberField label={`Weight for ${exerciseName}`} shortLabel="Weight" min={0} value={row.weight_kg} onChange={(value) => updateRow(index, { weight_kg: value }, setRows)} />
                <NumberField label={`Rest for ${exerciseName}`} shortLabel="Rest" min={0} value={row.rest_seconds} onChange={(value) => updateRow(index, { rest_seconds: value }, setRows)} />
              </div>
              <label className="mt-3 block">
                <span className="field-label">Coach cue</span>
                <textarea
                  aria-label={`Coach cue for ${exerciseName}`}
                  className="field-control min-h-20 resize-y"
                  placeholder="Cue, modification, tempo, or equipment note"
                  value={row.notes ?? ""}
                  onChange={(event) => updateRow(index, { notes: event.target.value }, setRows)}
                />
              </label>
            </div>
          );
        })}
      </div>
    </>
  );
}

function RowActions({ exerciseName, index, rows, setRows }: { exerciseName: string; index: number; rows: ProgramRow[]; setRows: SetRows }) {
  return (
    <div className="flex justify-end gap-1">
      <IconButton disabled={index === 0} label={`Move ${exerciseName} up`} onClick={() => moveRow(index, -1, setRows)}>
        <ArrowUp size={14} />
      </IconButton>
      <IconButton disabled={index === rows.length - 1} label={`Move ${exerciseName} down`} onClick={() => moveRow(index, 1, setRows)}>
        <ArrowDown size={14} />
      </IconButton>
      <IconButton disabled={rows.length <= 3} label={`Remove ${exerciseName}`} onClick={() => removeRow(index, setRows)}>
        <Trash2 size={14} />
      </IconButton>
    </div>
  );
}

function programExerciseToRow(program: Program["exercises"][number]): ProgramRow {
  return {
    exercise_id: program.exercise.id,
    sets: program.sets,
    reps: program.reps,
    weight_kg: program.weight_kg,
    rest_seconds: program.rest_seconds,
    notes: program.notes
  };
}

function programNotesForEditor(notes: string | null) {
  if (notes === "Built from the portfolio demo program builder.") return "";
  return notes ?? "";
}

function exerciseToDefaultRow(exercise: Exercise): ProgramRow {
  return {
    exercise_id: exercise.id,
    sets: 3,
    reps: exercise.category === "Core" ? 12 : 10,
    weight_kg: exercise.category === "Core" ? 0 : 20,
    rest_seconds: exercise.category === "Conditioning" ? 45 : 60,
    notes: null
  };
}

function normalizedRows(rows: ProgramRow[]) {
  return rows.map((row) => ({
    exercise_id: row.exercise_id,
    sets: row.sets,
    reps: row.reps,
    weight_kg: row.weight_kg,
    rest_seconds: row.rest_seconds,
    notes: row.notes?.trim() || null
  }));
}

function programSnapshot(name: string, focus: ProgramFocus | null, notes: string, rows: ProgramRow[]) {
  return JSON.stringify({
    name: name.trim(),
    focus,
    notes: notes.trim() || null,
    exercises: normalizedRows(rows)
  });
}

function getValidationMessages(name: string, rows: ProgramRow[]) {
  const messages: string[] = [];
  if (name.trim().length < 3) messages.push("Program name must be at least 3 characters.");
  if (rows.length < 3) messages.push("Program must include at least 3 exercises.");
  if (rows.length > 20) messages.push("Program can include up to 20 exercises.");
  if (rows.some((row) => !isValidRow(row))) messages.push("Every exercise needs valid sets, reps, weight, and rest.");
  return messages;
}

function isValidRow(row: ProgramRow) {
  return row.exercise_id > 0 && row.sets >= 1 && row.reps >= 1 && row.weight_kg >= 0 && row.rest_seconds >= 0;
}

function updateRow(index: number, patch: Partial<ProgramRow>, setRows: SetRows) {
  setRows((rows) => rows.map((row, rowIndex) => (rowIndex === index ? { ...row, ...patch } : row)));
}

function moveRow(index: number, direction: -1 | 1, setRows: SetRows) {
  setRows((rows) => {
    const next = [...rows];
    const target = index + direction;
    if (target < 0 || target >= next.length) return rows;
    [next[index], next[target]] = [next[target], next[index]];
    return next;
  });
}

function removeRow(index: number, setRows: SetRows) {
  setRows((rows) => rows.filter((_, rowIndex) => rowIndex !== index));
}

function NumberCell({ label, min, value, onChange }: { label: string; min: number; value: number; onChange: (value: number) => void }) {
  return (
    <input
      aria-label={label}
      className="w-full rounded-md border border-line bg-white px-2 py-2 text-right text-sm text-ink"
      min={min}
      type="number"
      value={value}
      onChange={(event) => onChange(Number(event.target.value))}
    />
  );
}

function NumberField({
  label,
  min,
  shortLabel,
  value,
  onChange
}: {
  label: string;
  min: number;
  shortLabel: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="block">
      <span className="field-label">{shortLabel}</span>
      <NumberCell label={label} min={min} value={value} onChange={onChange} />
    </label>
  );
}

function IconButton({ children, disabled, label, onClick }: { children: ReactNode; disabled?: boolean; label: string; onClick: () => void }) {
  return (
    <button
      aria-label={label}
      className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-line bg-white text-muted transition hover:bg-panel hover:text-ink disabled:cursor-not-allowed disabled:opacity-40 lg:h-9 lg:w-9"
      disabled={disabled}
      type="button"
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function exerciseMeta(exercise: Exercise | undefined) {
  if (!exercise) return "Exercise details unavailable";
  return `${exercise.category} - ${exercise.equipment}`;
}

function getSaveState({
  canSave,
  error,
  isDirty,
  isPending,
  isSuccess
}: {
  canSave: boolean;
  error: Error | null;
  isDirty: boolean;
  isPending: boolean;
  isSuccess: boolean;
}) {
  if (isPending) return { label: "saving", tone: "border-blue-200 bg-blue-50 text-brand" };
  if (error) return { label: "save failed", tone: "border-red-200 bg-red-50 text-danger" };
  if (!canSave) return { label: "needs fixes", tone: "border-amber-200 bg-amber-50 text-amber-900" };
  if (isDirty) return { label: "unsaved changes", tone: "border-amber-200 bg-amber-50 text-amber-900" };
  if (isSuccess) return { label: "saved", tone: "border-emerald-200 bg-emerald-50 text-success" };
  return { label: "saved", tone: "border-line bg-white text-muted" };
}
