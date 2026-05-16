"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowDown, ArrowUp, ClipboardCheck, Dumbbell, Plus, Save, Trash2, Users } from "lucide-react";
import { useMemo, useState } from "react";
import { api, type TrainingGroupPayload } from "@/lib/api";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { Client, Exercise, ProgramFocus, TrainingGroup } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";
import { MAX_COCKPIT_CLIENTS } from "@/components/dashboard/session-setup-model";

type GroupExerciseDraft = {
  exercise_id: number;
  sets: number;
  reps: number;
  weight_kg: number;
  rest_seconds: number;
  notes: string;
};

type GroupDraft = {
  name: string;
  focus: ProgramFocus;
  notes: string;
  client_ids: number[];
  exercises: GroupExerciseDraft[];
};

type DraftState = {
  mode: "create" | "edit";
  groupId?: number;
  draft: GroupDraft;
};

const FOCUS_OPTIONS: Array<{ label: string; value: ProgramFocus }> = [
  { label: "Strength", value: "Strength Block" },
  { label: "Endurance", value: "Conditioning Circuit" },
  { label: "Core", value: "Core Stability" }
];

const DEFAULT_EXERCISE_NAMES: Record<ProgramFocus, string[]> = {
  "Strength Block": ["Goblet Squat", "Dumbbell Bench Press", "Romanian Deadlift", "TRX Row"],
  "Conditioning Circuit": ["Bike Sprint", "Walking Lunge", "Farmer Carry", "Plank Hold"],
  "Core Stability": ["Dead Bug", "Pallof Press", "Step Up", "Tempo Split Squat"]
};

const EMPTY_GROUPS: TrainingGroup[] = [];
const EMPTY_CLIENTS: Client[] = [];
const EMPTY_EXERCISES: Exercise[] = [];

export function TrainingGroupsPanel({
  onPrepareGroup,
  variant = "full"
}: {
  onPrepareGroup?: (groupId: number) => void;
  variant?: "full" | "rail";
}) {
  const queryClient = useQueryClient();
  const groupsQuery = useQuery({ queryKey: ["groups"], queryFn: api.groups, retry: false });
  const clientsQuery = useQuery({ queryKey: ["clients"], queryFn: api.clients, retry: false });
  const exercisesQuery = useQuery({ queryKey: ["exercises"], queryFn: api.exercises, retry: false });
  const groups = groupsQuery.data ?? EMPTY_GROUPS;
  const clients = clientsQuery.data ?? EMPTY_CLIENTS;
  const exercises = exercisesQuery.data ?? EMPTY_EXERCISES;
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null);
  const [draftState, setDraftState] = useState<DraftState | null>(null);
  const [newExerciseId, setNewExerciseId] = useState<number | "">("");
  const selectedGroup = useMemo(
    () => groups.find((group) => group.id === selectedGroupId) ?? groups[0] ?? null,
    [groups, selectedGroupId]
  );
  const isRail = variant === "rail";

  const save = useMutation({
    mutationFn: ({ groupId, draft }: { groupId?: number; draft: GroupDraft }) => {
      const payload = draftToPayload(draft);
      return groupId ? api.updateGroup(groupId, payload) : api.createGroup(payload);
    },
    onSuccess: (group) => {
      setSelectedGroupId(group.id);
      setDraftState(null);
      queryClient.invalidateQueries({ queryKey: ["groups"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    }
  });

  const remove = useMutation({
    mutationFn: api.deleteGroup,
    onSuccess: () => {
      setSelectedGroupId(null);
      setDraftState(null);
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    }
  });

  function openCreate() {
    setNewExerciseId("");
    setDraftState({ mode: "create", draft: createDefaultDraft(exercises) });
  }

  function openEdit(group: TrainingGroup) {
    setNewExerciseId("");
    setDraftState({ mode: "edit", groupId: group.id, draft: draftFromGroup(group) });
  }

  function deleteDraftGroup() {
    const groupId = draftState?.groupId;
    if (!groupId) return;
    if (window.confirm("Archive this saved group?")) remove.mutate(groupId);
  }

  const error = groupsQuery.error ?? clientsQuery.error ?? exercisesQuery.error ?? save.error ?? remove.error;

  return (
    <Card className={isRail ? "shrink-0 overflow-hidden border-brand/20" : "flex min-h-[260px] flex-1 flex-col overflow-hidden border-brand/20"} id="groups">
      <CardHeader className={isRail ? "px-3 py-1.5" : "px-3 py-2.5"}>
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold text-ink">Saved groups</h2>
            <p className="text-xs text-muted">{isRail ? "Pick a preset, then prepare" : "Reusable rosters and workouts"}</p>
          </div>
          {isRail ? (
            <a
              aria-label="Manage saved groups"
              className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line bg-white text-ink shadow-sm transition hover:bg-panel"
              href={routes.groups}
            >
              <Plus size={14} />
            </a>
          ) : (
            <Button aria-label="Create group" size="sm" variant="secondary" onClick={openCreate}>
              <Plus size={14} />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardBody className={isRail ? "space-y-1.5 p-2" : "subtle-scrollbar min-h-0 flex-1 space-y-3 overflow-y-auto p-3"}>
        {groupsQuery.isLoading ? <p className="text-sm text-muted">Loading groups...</p> : null}
        {error && <p className="rounded-md bg-red-50 p-2 text-sm text-danger">{getErrorMessage(error)}</p>}

        {isRail ? (
          <CompactGroups
            groups={groups}
            selectedGroup={selectedGroup}
            onPrepareGroup={onPrepareGroup}
            onSelectGroup={setSelectedGroupId}
          />
        ) : draftState ? (
          <GroupEditor
            clients={clients}
            draftState={draftState}
            exercises={exercises}
            isSaving={save.isPending}
            newExerciseId={newExerciseId}
            onCancel={() => setDraftState(null)}
            onDelete={draftState.groupId ? deleteDraftGroup : undefined}
            onNewExerciseIdChange={setNewExerciseId}
            onSave={() => save.mutate({ groupId: draftState.groupId, draft: draftState.draft })}
            onUpdate={setDraftState}
          />
        ) : (
          <>
            <div className="space-y-1.5">
              {groups.map((group) => (
                <button
                  aria-pressed={selectedGroup?.id === group.id}
                  className={`w-full rounded-md border px-2.5 py-2 text-left transition ${
                    selectedGroup?.id === group.id ? "border-brand/40 bg-blue-50/70" : "border-line bg-white hover:bg-panel"
                  }`}
                  key={group.id}
                  type="button"
                  onClick={() => setSelectedGroupId(group.id)}
                >
                  <span className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm font-bold text-ink">{group.name}</span>
                    <span className={focusPillClassName(group.focus)}>{focusLabel(group.focus)}</span>
                  </span>
                  <span className="mt-1 flex items-center gap-2 text-xs text-muted">
                    <Users size={13} />
                    {group.clients.length} clients
                    <Dumbbell size={13} />
                    {group.exercises.length} exercises
                  </span>
                </button>
              ))}
              {groups.length === 0 && !groupsQuery.isLoading && (
                <p className="rounded-md border border-dashed border-line bg-white px-3 py-3 text-sm text-muted">
                  Create a saved group for a recurring strength, endurance, or core session.
                </p>
              )}
            </div>

            {selectedGroup && (
              <GroupSummary
                group={selectedGroup}
                onEdit={() => openEdit(selectedGroup)}
                onPrepare={onPrepareGroup ? () => onPrepareGroup(selectedGroup.id) : undefined}
              />
            )}
          </>
        )}
      </CardBody>
    </Card>
  );
}

function CompactGroups({
  groups,
  selectedGroup,
  onPrepareGroup,
  onSelectGroup
}: {
  groups: TrainingGroup[];
  selectedGroup: TrainingGroup | null;
  onPrepareGroup?: (groupId: number) => void;
  onSelectGroup: (groupId: number) => void;
}) {
  if (groups.length === 0) {
    return (
      <p className="rounded-md border border-dashed border-line bg-white px-3 py-2 text-xs font-semibold text-muted">
        No saved groups yet.
      </p>
    );
  }

  return (
    <>
      <div className="grid gap-1">
        {groups.map((group) => (
          <button
            aria-pressed={selectedGroup?.id === group.id}
            className={`grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 rounded-md border px-2 py-1 text-left transition ${
              selectedGroup?.id === group.id ? "border-brand/40 bg-blue-50/70" : "border-line bg-white hover:bg-panel"
            }`}
            key={group.id}
            type="button"
            onClick={() => onSelectGroup(group.id)}
          >
            <span className="min-w-0">
              <span className="block truncate text-[12px] font-bold leading-4 text-ink">{group.name}</span>
              <span className="flex items-center gap-1.5 text-[10px] font-semibold text-muted">
                <Users size={11} />
                {group.clients.length}
                <Dumbbell size={11} />
                {group.exercises.length}
              </span>
            </span>
            <span className={compactFocusPillClassName(group.focus)}>{focusLabel(group.focus)}</span>
          </button>
        ))}
      </div>

      {selectedGroup ? (
        <section className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 rounded-md border border-line bg-white/85 p-2">
          <div className="min-w-0">
            <p className="text-[9px] font-bold uppercase leading-3 text-muted">Selected group</p>
            <p className="truncate text-[12px] font-bold leading-4 text-ink">{selectedGroup.name}</p>
            <p className="truncate text-[11px] font-semibold text-muted">
              {selectedGroup.clients.length}/{MAX_COCKPIT_CLIENTS} clients
              <span className="sr-only">: {selectedGroup.clients.map((client) => client.name).join(", ")}</span>
            </p>
          </div>
          {onPrepareGroup ? (
            <Button
              aria-label={`Prepare ${selectedGroup.name}`}
              className="min-h-7 px-2 py-1 text-[11px]"
              size="sm"
              onClick={() => onPrepareGroup(selectedGroup.id)}
            >
              <ClipboardCheck size={12} />
              Prepare
            </Button>
          ) : (
            <a
              aria-label={`Open setup for ${selectedGroup.name}`}
              className="inline-flex min-h-7 items-center justify-center gap-1.5 rounded-md bg-brand px-2 py-1 text-[11px] font-semibold text-white transition hover:bg-blue-700"
              href="/dashboard#live-session"
            >
              <ClipboardCheck size={12} />
              Setup
            </a>
          )}
        </section>
      ) : null}
    </>
  );
}

function GroupSummary({
  group,
  onEdit,
  onPrepare
}: {
  group: TrainingGroup;
  onEdit: () => void;
  onPrepare?: () => void;
}) {
  return (
    <section className="rounded-md border border-line bg-white/80 p-2.5">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="field-label">Selected group</p>
          <p className="text-sm font-bold text-ink">{group.name}</p>
        </div>
        <span className={focusPillClassName(group.focus)}>{focusLabel(group.focus)}</span>
      </div>
      {group.notes && <p className="mt-2 line-clamp-2 text-xs leading-5 text-muted">{group.notes}</p>}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {group.clients.map((client) => (
          <span className="inline-flex items-center gap-1 rounded-full bg-panel px-2 py-1 text-xs font-semibold text-muted" key={client.id}>
            <ClientAvatar className="h-5 w-5 rounded text-[9px]" name={client.name} size="sm" />
            {client.name}
          </span>
        ))}
      </div>
      <div className="mt-3 space-y-1">
        {group.exercises.slice(0, 4).map((item, index) => (
          <div className="grid grid-cols-[22px_1fr_auto] items-center gap-2 text-xs" key={item.id}>
            <span className="text-muted">{index + 1}</span>
            <span className="truncate font-semibold text-ink">{item.exercise.name}</span>
            <span className="text-muted">{item.sets}x{item.reps}</span>
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2">
        <Button aria-label={`Manage ${group.name}`} size="sm" variant="secondary" onClick={onEdit}>
          Manage
        </Button>
        {onPrepare ? (
          <Button aria-label={`Prepare ${group.name}`} size="sm" onClick={onPrepare}>
            <ClipboardCheck size={14} />
            Prepare
          </Button>
        ) : (
          <a
            aria-label={`Open setup for ${group.name}`}
            className="inline-flex min-h-9 items-center justify-center gap-2 rounded-md bg-brand px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
            href="/dashboard#live-session"
          >
            <ClipboardCheck size={14} />
            Setup
          </a>
        )}
      </div>
    </section>
  );
}

function GroupEditor({
  clients,
  draftState,
  exercises,
  isSaving,
  newExerciseId,
  onCancel,
  onDelete,
  onNewExerciseIdChange,
  onSave,
  onUpdate
}: {
  clients: Client[];
  draftState: DraftState;
  exercises: Exercise[];
  isSaving: boolean;
  newExerciseId: number | "";
  onCancel: () => void;
  onDelete?: () => void;
  onNewExerciseIdChange: (value: number | "") => void;
  onSave: () => void;
  onUpdate: (state: DraftState) => void;
}) {
  const draft = draftState.draft;
  const canSave =
    draft.name.trim().length >= 3 &&
    draft.client_ids.length >= 1 &&
    draft.client_ids.length <= MAX_COCKPIT_CLIENTS &&
    draft.exercises.length >= 3;

  function patchDraft(patch: Partial<GroupDraft>) {
    onUpdate({ ...draftState, draft: { ...draft, ...patch } });
  }

  function toggleClient(clientId: number) {
    const isSelected = draft.client_ids.includes(clientId);
    if (isSelected) {
      patchDraft({ client_ids: draft.client_ids.filter((id) => id !== clientId) });
      return;
    }
    if (draft.client_ids.length >= MAX_COCKPIT_CLIENTS) return;
    patchDraft({ client_ids: [...draft.client_ids, clientId] });
  }

  function updateExercise(index: number, patch: Partial<GroupExerciseDraft>) {
    patchDraft({ exercises: draft.exercises.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item)) });
  }

  function addExercise() {
    const selectedId = Number(newExerciseId) || exercises.find((exercise) => !draft.exercises.some((item) => item.exercise_id === exercise.id))?.id || exercises[0]?.id;
    if (!selectedId) return;
    patchDraft({
      exercises: [
        ...draft.exercises,
        {
          exercise_id: selectedId,
          sets: 3,
          reps: 10,
          weight_kg: 0,
          rest_seconds: 60,
          notes: ""
        }
      ]
    });
    onNewExerciseIdChange("");
  }

  function moveExercise(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= draft.exercises.length) return;
    const next = [...draft.exercises];
    [next[index], next[target]] = [next[target], next[index]];
    patchDraft({ exercises: next });
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="field-label">{draftState.mode === "create" ? "New group" : "Edit group"}</p>
          <p className="text-sm font-bold text-ink">{draftState.mode === "create" ? "Build reusable roster" : "Manage saved plan"}</p>
        </div>
        <Button size="sm" variant="ghost" onClick={onCancel}>
          Close
        </Button>
      </div>

      <label className="block">
        <span className="field-label">Group name</span>
        <input className="field-control" value={draft.name} onChange={(event) => patchDraft({ name: event.target.value })} />
      </label>
      <label className="block">
        <span className="field-label">Focus</span>
        <select className="field-control" value={draft.focus} onChange={(event) => patchDraft({ focus: event.target.value as ProgramFocus })}>
          {FOCUS_OPTIONS.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
      <label className="block">
        <span className="field-label">Coach note</span>
        <textarea className="field-control min-h-16 resize-none" value={draft.notes} onChange={(event) => patchDraft({ notes: event.target.value })} />
      </label>

      <section>
        <div className="mb-1.5 flex items-center justify-between">
          <p className="field-label">Members</p>
          <span className="rounded-full bg-panel px-2 py-1 text-[10px] font-bold uppercase text-muted">
            {draft.client_ids.length}/{MAX_COCKPIT_CLIENTS}
          </span>
        </div>
        <div className="subtle-scrollbar grid max-h-36 gap-1 overflow-y-auto pr-1">
          {clients.map((client) => {
            const selected = draft.client_ids.includes(client.id);
            return (
              <button
                aria-pressed={selected}
                className={`grid grid-cols-[28px_1fr] items-center gap-2 rounded-md border px-2 py-1.5 text-left transition ${
                  selected ? "border-brand bg-blue-50 text-ink" : "border-line bg-white text-muted hover:bg-panel hover:text-ink"
                }`}
                disabled={!selected && draft.client_ids.length >= MAX_COCKPIT_CLIENTS}
                key={client.id}
                type="button"
                onClick={() => toggleClient(client.id)}
              >
                <ClientAvatar name={client.name} size="sm" />
                <span className="truncate text-xs font-bold">{client.name}</span>
              </button>
            );
          })}
        </div>
      </section>

      <section>
        <div className="mb-1.5 flex items-center justify-between">
          <p className="field-label">Exercises</p>
          <span className="rounded-full bg-panel px-2 py-1 text-[10px] font-bold uppercase text-muted">{draft.exercises.length}</span>
        </div>
        <div className="space-y-1.5">
          {draft.exercises.map((item, index) => (
            <div className="rounded-md border border-line bg-white p-2" key={`${item.exercise_id}-${index}`}>
              <div className="grid grid-cols-[1fr_auto_auto_auto] items-center gap-1">
                <select
                  aria-label={`Exercise ${index + 1}`}
                  className="min-w-0 rounded-md border border-line bg-white px-2 py-1.5 text-xs font-semibold text-ink"
                  value={item.exercise_id}
                  onChange={(event) => updateExercise(index, { exercise_id: Number(event.target.value) })}
                >
                  {exercises.map((exercise) => (
                    <option key={exercise.id} value={exercise.id}>
                      {exercise.name}
                    </option>
                  ))}
                </select>
                <IconButton ariaLabel={`Move exercise ${index + 1} up`} disabled={index === 0} icon={<ArrowUp size={13} />} onClick={() => moveExercise(index, -1)} />
                <IconButton ariaLabel={`Move exercise ${index + 1} down`} disabled={index === draft.exercises.length - 1} icon={<ArrowDown size={13} />} onClick={() => moveExercise(index, 1)} />
                <IconButton ariaLabel={`Remove exercise ${index + 1}`} disabled={draft.exercises.length <= 3} icon={<Trash2 size={13} />} onClick={() => patchDraft({ exercises: draft.exercises.filter((_, itemIndex) => itemIndex !== index) })} />
              </div>
              <div className="mt-1.5 grid grid-cols-4 gap-1">
                <NumberField label="Sets" value={item.sets} onChange={(value) => updateExercise(index, { sets: value })} />
                <NumberField label="Reps" value={item.reps} onChange={(value) => updateExercise(index, { reps: value })} />
                <NumberField label="Kg" step={0.5} value={item.weight_kg} onChange={(value) => updateExercise(index, { weight_kg: value })} />
                <NumberField label="Rest" value={item.rest_seconds} onChange={(value) => updateExercise(index, { rest_seconds: value })} />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-2 grid grid-cols-[1fr_auto] gap-2">
          <select
            aria-label="Exercise to add"
            className="rounded-md border border-line bg-white px-2 py-2 text-xs font-semibold text-ink"
            value={newExerciseId}
            onChange={(event) => onNewExerciseIdChange(event.target.value ? Number(event.target.value) : "")}
          >
            <option value="">Choose exercise</option>
            {exercises.map((exercise) => (
              <option key={exercise.id} value={exercise.id}>
                {exercise.name}
              </option>
            ))}
          </select>
          <Button aria-label="Add exercise to group" size="sm" variant="secondary" onClick={addExercise}>
            <Plus size={13} />
          </Button>
        </div>
      </section>

      <div className="grid grid-cols-[1fr_auto] gap-2">
        <Button disabled={!canSave || isSaving} size="sm" onClick={onSave}>
          <Save size={14} />
          {isSaving ? "Saving..." : "Save"}
        </Button>
        {onDelete && (
          <Button aria-label="Delete group" size="sm" variant="danger" onClick={onDelete}>
            <Trash2 size={14} />
          </Button>
        )}
      </div>
      {!canSave && (
        <p className="rounded-md bg-amber-50 p-2 text-xs font-semibold text-warning">
          Use 1-{MAX_COCKPIT_CLIENTS} members and at least 3 exercises.
        </p>
      )}
    </section>
  );
}

function NumberField({ label, step = 1, value, onChange }: { label: string; step?: number; value: number; onChange: (value: number) => void }) {
  return (
    <label className="block">
      <span className="text-[10px] font-bold uppercase text-muted">{label}</span>
      <input
        className="mt-0.5 w-full rounded-md border border-line px-1.5 py-1 text-xs font-semibold text-ink"
        min={0}
        step={step}
        type="number"
        value={value}
        onChange={(event) => onChange(Math.max(0, Number(event.target.value) || 0))}
      />
    </label>
  );
}

function IconButton({ ariaLabel, disabled, icon, onClick }: { ariaLabel: string; disabled?: boolean; icon: React.ReactNode; onClick: () => void }) {
  return (
    <button
      aria-label={ariaLabel}
      className="inline-flex h-7 w-7 items-center justify-center rounded-md border border-line text-muted transition hover:bg-panel hover:text-ink disabled:cursor-not-allowed disabled:opacity-35"
      disabled={disabled}
      type="button"
      onClick={onClick}
    >
      {icon}
    </button>
  );
}

function createDefaultDraft(exercises: Exercise[]): GroupDraft {
  const focus: ProgramFocus = "Strength Block";
  return {
    name: "New Strength Group",
    focus,
    notes: "",
    client_ids: [],
    exercises: defaultExerciseDrafts(exercises, focus)
  };
}

function draftFromGroup(group: TrainingGroup): GroupDraft {
  return {
    name: group.name,
    focus: group.focus ?? "Strength Block",
    notes: group.notes ?? "",
    client_ids: group.clients.map((client) => client.id),
    exercises: group.exercises.map((item) => ({
      exercise_id: item.exercise.id,
      sets: item.sets,
      reps: item.reps,
      weight_kg: item.weight_kg,
      rest_seconds: item.rest_seconds,
      notes: item.notes ?? ""
    }))
  };
}

function defaultExerciseDrafts(exercises: Exercise[], focus: ProgramFocus): GroupExerciseDraft[] {
  const byName = new Map(exercises.map((exercise) => [exercise.name, exercise]));
  const preferred = DEFAULT_EXERCISE_NAMES[focus].map((name) => byName.get(name)).filter((exercise): exercise is Exercise => Boolean(exercise));
  const selected = preferred.length >= 3 ? preferred : exercises.slice(0, 4);
  return selected.map((exercise, index) => ({
    exercise_id: exercise.id,
    sets: 3,
    reps: focus === "Conditioning Circuit" && index === 0 ? 12 : 8 + index * 2,
    weight_kg: focus === "Core Stability" ? 0 : 16 + index * 4,
    rest_seconds: 45 + index * 15,
    notes: ""
  }));
}

function draftToPayload(draft: GroupDraft): TrainingGroupPayload {
  return {
    name: draft.name.trim(),
    focus: draft.focus,
    notes: draft.notes.trim() || null,
    client_ids: draft.client_ids,
    exercises: draft.exercises.map((item) => ({
      exercise_id: item.exercise_id,
      sets: Math.max(1, Math.round(item.sets)),
      reps: Math.max(1, Math.round(item.reps)),
      weight_kg: Math.max(0, item.weight_kg),
      rest_seconds: Math.max(0, Math.round(item.rest_seconds)),
      notes: item.notes?.trim() || null
    }))
  };
}

function focusLabel(focus: ProgramFocus | null) {
  return FOCUS_OPTIONS.find((item) => item.value === focus)?.label ?? "Custom";
}

function focusPillClassName(focus: ProgramFocus | null) {
  const base = "rounded-full border px-2 py-1 text-[10px] font-bold uppercase";
  if (focus === "Conditioning Circuit") return `${base} border-amber-200 bg-amber-50 text-warning`;
  if (focus === "Core Stability") return `${base} border-emerald-200 bg-emerald-50 text-success`;
  return `${base} border-blue-200 bg-blue-50 text-brand`;
}

function compactFocusPillClassName(focus: ProgramFocus | null) {
  const base = "rounded-full border px-1.5 py-0.5 text-[9px] font-bold uppercase leading-4";
  if (focus === "Conditioning Circuit") return `${base} border-amber-200 bg-amber-50 text-warning`;
  if (focus === "Core Stability") return `${base} border-emerald-200 bg-emerald-50 text-success`;
  return `${base} border-blue-200 bg-blue-50 text-brand`;
}
