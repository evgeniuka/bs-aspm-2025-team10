"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Dumbbell, Play, Search, ShieldCheck, TimerReset, UserCheck, UserPlus, UserX, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { Client, ClientReadiness, Program, TrainingGroup, TrainingSession } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientSessionBlock } from "@/components/dashboard/client-session-block";
import {
  buildClientProgramOptions,
  buildSessionPayload,
  ctaLabel,
  DEFAULT_SESSION_FOCUS,
  MAX_COCKPIT_CLIENTS,
  programVariantName,
  resolveProgram,
  SESSION_FOCI,
  type ClientProgramOptions,
  type SessionAssignment,
  type SessionFocus
} from "@/components/dashboard/session-setup-model";
import { ClientAvatar } from "@/components/ui/client-avatar";

const GROUP_TEMPLATE_VALUE = "group-template" as const;
type ProgramSelection = number | typeof GROUP_TEMPLATE_VALUE;

export function StartSessionPanel({
  activeSession,
  groupPresetId,
  readiness,
  onGroupPresetHandled
}: {
  activeSession: TrainingSession | null;
  groupPresetId?: number | null;
  readiness: ClientReadiness[];
  onGroupPresetHandled?: () => void;
}) {
  const queryClient = useQueryClient();
  const [selectedClientIds, setSelectedClientIds] = useState<number[]>([]);
  const [programByClientId, setProgramByClientId] = useState<Record<number, ProgramSelection>>({});
  const [clientSearch, setClientSearch] = useState("");
  const [sessionFocus, setSessionFocus] = useState<SessionFocus>(DEFAULT_SESSION_FOCUS);
  const [selectedGroupId, setSelectedGroupId] = useState<number | "">("");
  const clientsQuery = useQuery({ queryKey: ["clients"], queryFn: api.clients, retry: false });
  const programsQuery = useQuery({ queryKey: ["programs"], queryFn: () => api.programs(), retry: false });
  const groupsQuery = useQuery({ queryKey: ["groups"], queryFn: api.groups, retry: false });
  const isPreparing = clientsQuery.isLoading || programsQuery.isLoading;
  const clientProgramOptions = useMemo(() => buildClientProgramOptions(clientsQuery.data ?? [], programsQuery.data ?? []), [clientsQuery.data, programsQuery.data]);
  const savedGroups = useMemo(() => groupsQuery.data ?? [], [groupsQuery.data]);
  const selectedGroup = selectedGroupId ? savedGroups.find((group) => group.id === selectedGroupId) ?? null : null;
  const readinessByClientId = useMemo<Record<number, ClientReadiness>>(
    () => Object.fromEntries(readiness.map((item) => [item.client.id, item])),
    [readiness]
  );
  const selectedAssignments = useMemo(
    () =>
      selectedClientIds
        .map((clientId) => {
          const option = clientProgramOptions.find((item) => item.client.id === clientId);
          if (!option) return null;
          const program = resolveAssignmentProgram(option.client, option.programs, sessionFocus, selectedGroup, programByClientId[clientId]);
          return program ? { client: option.client, program } : null;
        })
        .filter((item): item is SessionAssignment => Boolean(item)),
    [clientProgramOptions, programByClientId, selectedClientIds, selectedGroup, sessionFocus]
  );
  const availableClients = clientProgramOptions.filter((option) => !selectedClientIds.includes(option.client.id));
  const selectedCount = selectedClientIds.length;
  const canStart =
    Boolean(activeSession) ||
    (!isPreparing && selectedCount >= 1 && selectedCount <= MAX_COCKPIT_CLIENTS && selectedAssignments.length === selectedCount);

  const start = useMutation({
    mutationFn: () =>
      selectedGroup
        ? api.startGroupSession(selectedGroup.id, {
            clients: selectedClientIds.map((clientId) => ({
              client_id: clientId,
              program_id: programByClientId[clientId] && programByClientId[clientId] !== GROUP_TEMPLATE_VALUE ? Number(programByClientId[clientId]) : null
            }))
          })
        : api.startSession(buildSessionPayload(selectedAssignments)),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      window.location.assign(routes.session(data.session_id));
    }
  });

  function openCockpit() {
    if (activeSession) {
      window.location.assign(routes.session(activeSession.id));
      return;
    }
    if (!canStart || start.isPending) return;
    start.mutate();
  }

  function addClient(clientId: number) {
    if (selectedClientIds.includes(clientId) || selectedClientIds.length >= MAX_COCKPIT_CLIENTS) return;
    setSelectedClientIds([...selectedClientIds, clientId]);
  }

  function removeClient(clientId: number) {
    setSelectedClientIds(selectedClientIds.filter((selectedClientId) => selectedClientId !== clientId));
  }

  function selectSolo(clientId: number) {
    setSelectedClientIds([clientId]);
  }

  function toggleGroupMember(clientId: number) {
    if (selectedClientIds.includes(clientId)) {
      removeClient(clientId);
      return;
    }
    addClient(clientId);
  }

  function clearLineup() {
    setSelectedGroupId("");
    setSelectedClientIds([]);
  }

  function applyFocus(focus: SessionFocus) {
    setSessionFocus(focus);
    setProgramByClientId({});
  }

  function selectProgram(clientId: number, programId: ProgramSelection) {
    setProgramByClientId((current) => ({ ...current, [clientId]: programId }));
  }

  const selectSavedGroup = useCallback((groupId: number | "") => {
    setSelectedGroupId(groupId);
    if (!groupId) return;
    const group = savedGroups.find((item) => item.id === groupId);
    if (!group) return;
    const selectableClientIds = new Set(clientProgramOptions.map((item) => item.client.id));
    setSelectedClientIds(group.clients.map((client) => client.id).filter((clientId) => selectableClientIds.has(clientId)).slice(0, MAX_COCKPIT_CLIENTS));
    if (isSessionFocus(group.focus)) setSessionFocus(group.focus);
    setProgramByClientId({});
    setClientSearch("");
  }, [clientProgramOptions, savedGroups]);

  useEffect(() => {
    if (!groupPresetId || isPreparing || groupsQuery.isLoading) return;
    const id = window.setTimeout(() => {
      selectSavedGroup(groupPresetId);
      onGroupPresetHandled?.();
      document.getElementById("live-session")?.scrollIntoView({ block: "start" });
    }, 0);
    return () => window.clearTimeout(id);
  }, [groupPresetId, groupsQuery.isLoading, isPreparing, onGroupPresetHandled, selectSavedGroup]);

  const startError = start.error ? getErrorMessage(start.error) : null;
  const dataError = clientsQuery.error ?? programsQuery.error ?? groupsQuery.error;

  return (
    <Card className="visual-card flex h-full min-h-0 flex-col overflow-hidden border-brand/20 shadow-elevated">
      <CardHeader className="shrink-0 bg-white/75 px-3 py-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="field-label">Today</p>
            <h2 className="text-lg font-bold tracking-tight text-ink">Build today&apos;s session</h2>
            <p className="mt-0.5 hidden text-sm text-muted min-[900px]:block">Attendance first, one workout focus, then start coaching.</p>
          </div>
          <div className="flex items-center gap-2">
            <SavedGroupSelect groups={savedGroups} isLoading={groupsQuery.isLoading} selectedGroupId={selectedGroupId} onSelect={selectSavedGroup} />
            <button
              className="rounded-full border border-line bg-white px-3 py-1.5 text-xs font-bold uppercase text-muted transition hover:bg-panel disabled:cursor-not-allowed disabled:opacity-50"
              disabled={selectedCount === 0}
              type="button"
              onClick={clearLineup}
            >
              Clear
            </button>
            <span className="status-pill">{activeSession ? "active" : isPreparing ? "loading" : `${selectedCount}/${MAX_COCKPIT_CLIENTS} selected`}</span>
          </div>
        </div>
      </CardHeader>

      <CardBody className="flex min-h-0 flex-1 flex-col p-0">
        <div className="subtle-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
          {activeSession ? (
            <ActiveSessionResume activeSession={activeSession} />
          ) : (
            <div className="grid min-h-full gap-3 min-[560px]:grid-cols-[minmax(238px,0.95fr)_minmax(238px,1.05fr)] xl:grid-cols-[minmax(320px,0.9fr)_minmax(0,1.1fr)]">
              <ClientPicker
                clients={availableClients}
                isLoading={isPreparing}
                maxClients={MAX_COCKPIT_CLIENTS}
                readinessByClientId={readinessByClientId}
                searchQuery={clientSearch}
                selectedCount={selectedCount}
                onAdd={addClient}
                onSearchChange={setClientSearch}
                onSolo={selectSolo}
              />

              <section className="min-h-0 space-y-3">
                {selectedGroup ? (
                  <GroupSessionTunnel
                    assignments={selectedAssignments}
                    group={selectedGroup}
                    selectedClientIds={selectedClientIds}
                    onToggleMember={toggleGroupMember}
                  />
                ) : null}
                <PresentLineup
                  assignments={selectedAssignments}
                  clientProgramOptions={clientProgramOptions}
                  programByClientId={programByClientId}
                  selectedGroup={selectedGroup}
                  onRemove={removeClient}
                  onSelectProgram={selectProgram}
                />
                {selectedGroup ? null : (
                  <>
                    <ClientSessionBlock assignments={selectedAssignments} />
                    <FocusSelector focus={sessionFocus} onChange={applyFocus} />
                  </>
                )}
              </section>
            </div>
          )}
        </div>

        <div className="shrink-0 space-y-2 border-t border-line/80 bg-white/90 p-3">
          {dataError && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{getErrorMessage(dataError)}</p>}
          {startError && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{startError}</p>}
          <Button className="w-full" disabled={isPreparing || !canStart || start.isPending} onClick={openCockpit}>
            <Play size={16} />
            {ctaLabel({ activeSession, isPreparing, isPending: start.isPending, selectedCount })}
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}

function SavedGroupSelect({
  groups,
  isLoading,
  selectedGroupId,
  onSelect
}: {
  groups: TrainingGroup[];
  isLoading: boolean;
  selectedGroupId: number | "";
  onSelect: (groupId: number | "") => void;
}) {
  return (
    <label className="min-w-[172px]" id="session-groups" tabIndex={-1}>
      <span className="sr-only">Saved group preset</span>
      <select
        aria-label="Saved group preset"
        className="h-8 w-full rounded-full border border-line bg-white px-3 text-xs font-bold uppercase text-muted transition hover:bg-panel focus:border-brand"
        disabled={isLoading || groups.length === 0}
        value={selectedGroupId}
        onChange={(event) => onSelect(event.target.value ? Number(event.target.value) : "")}
      >
        <option value="">{isLoading ? "Loading groups" : "Choose group"}</option>
        {groups.map((group) => (
          <option key={group.id} value={group.id}>
            {group.name} - {group.clients.length}
          </option>
        ))}
      </select>
    </label>
  );
}

function GroupSessionTunnel({
  assignments,
  group,
  selectedClientIds,
  onToggleMember
}: {
  assignments: SessionAssignment[];
  group: TrainingGroup;
  selectedClientIds: number[];
  onToggleMember: (clientId: number) => void;
}) {
  const selected = new Set(selectedClientIds);
  const groupClientIds = new Set(group.clients.map((client) => client.id));
  const substitutes = assignments.filter((assignment) => !groupClientIds.has(assignment.client.id));
  const totalSets = group.exercises.reduce((sum, item) => sum + item.sets, 0);
  const canAddMore = selectedClientIds.length < MAX_COCKPIT_CLIENTS;

  return (
    <section className="rounded-md border border-brand/20 bg-blue-50/40 p-2.5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="field-label">Group session</p>
          <h3 className="text-sm font-bold text-ink">{group.name}</h3>
          <p className="mt-0.5 text-xs text-muted">{group.notes ?? "Confirm attendance and use the saved group template."}</p>
        </div>
        <span className="rounded-full border border-blue-200 bg-white px-2.5 py-1 text-xs font-bold uppercase text-brand">
          {group.focus ?? "Custom"}
        </span>
      </div>

      <div className="mt-3 grid gap-3 min-[900px]:grid-cols-[minmax(0,1fr)_minmax(190px,0.8fr)]">
        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <p className="field-label">Attendance</p>
            <span className="text-xs font-bold text-muted">
              {group.clients.filter((client) => selected.has(client.id)).length}/{group.clients.length} present
            </span>
          </div>
          <div className="grid gap-1.5">
            {group.clients.map((client) => {
              const isPresent = selected.has(client.id);
              return (
                <button
                  aria-pressed={isPresent}
                  className={`grid grid-cols-[30px_minmax(0,1fr)_auto] items-center gap-2 rounded-md border px-2 py-1.5 text-left transition ${
                    isPresent ? "border-emerald-200 bg-white text-ink" : "border-line bg-white/70 text-muted hover:bg-white"
                  }`}
                  disabled={!isPresent && !canAddMore}
                  key={client.id}
                  type="button"
                  onClick={() => onToggleMember(client.id)}
                >
                  <ClientAvatar name={client.name} size="sm" />
                  <span className="min-w-0">
                    <span className="block truncate text-xs font-bold">{client.name}</span>
                    <span className="block text-[11px]">{isPresent ? "Present" : canAddMore ? "Absent" : "Cockpit full"}</span>
                  </span>
                  <span className={isPresent ? "text-success" : "text-muted"}>{isPresent ? <UserCheck size={15} /> : <UserX size={15} />}</span>
                </button>
              );
            })}
          </div>
          {substitutes.length > 0 ? (
            <div className="mt-2 rounded-md border border-amber-200 bg-amber-50 px-2 py-1.5 text-xs font-semibold text-warning">
              Substitute: {substitutes.map((item) => item.client.name).join(", ")}
            </div>
          ) : null}
        </div>

        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <p className="field-label">Template</p>
            <span className="rounded-full bg-white px-2 py-0.5 text-[10px] font-bold uppercase text-muted">{totalSets} sets</span>
          </div>
          <div className="grid gap-1.5">
            {group.exercises.slice(0, 5).map((item, index) => (
              <div className="grid grid-cols-[22px_1fr_auto] items-center gap-2 rounded-md border border-line bg-white px-2 py-1.5 text-xs" key={item.id}>
                <span className="flex h-5 w-5 items-center justify-center rounded bg-panel text-[10px] font-bold text-muted">{index + 1}</span>
                <span className="min-w-0">
                  <span className="block truncate font-bold text-ink">{item.exercise.name}</span>
                  <span className="text-muted">{item.weight_kg ? `${item.weight_kg}kg` : "bodyweight"} - {item.rest_seconds}s rest</span>
                </span>
                <span className="font-bold text-muted">{item.sets}x{item.reps}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function FocusSelector({ focus, onChange }: { focus: SessionFocus; onChange: (focus: SessionFocus) => void }) {
  return (
    <section>
      <div className="mb-2">
        <p className="field-label">Focus</p>
        <p className="text-xs text-muted">Applies matching plans.</p>
      </div>
      <div className="grid overflow-hidden rounded-md border border-line bg-white sm:grid-cols-3">
        {SESSION_FOCI.map((item) => (
          <button
            aria-pressed={focus === item.value}
            className={`border-b border-line px-3 py-3 text-left transition last:border-b-0 sm:border-b-0 sm:border-r sm:last:border-r-0 ${focusButtonClassName(item.value, focus === item.value)}`}
            key={item.value}
            type="button"
            onClick={() => onChange(item.value)}
          >
            <span className="flex items-center gap-2 text-sm font-bold">
              <FocusIcon focus={item.value} />
              {item.label}
            </span>
            <span className="mt-0.5 block text-xs">{item.description}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function PresentLineup({
  assignments,
  clientProgramOptions,
  programByClientId,
  selectedGroup,
  onRemove,
  onSelectProgram
}: {
  assignments: SessionAssignment[];
  clientProgramOptions: ClientProgramOptions[];
  programByClientId: Record<number, ProgramSelection>;
  selectedGroup: TrainingGroup | null;
  onRemove: (clientId: number) => void;
  onSelectProgram: (clientId: number, programId: ProgramSelection) => void;
}) {
  return (
    <section className="rounded-md border border-line bg-white/70 p-2.5" id="programs" tabIndex={-1}>
      <div className="mb-2">
        <p className="field-label">Selected for session</p>
        <p className="text-xs text-muted">{assignments.length === 0 ? "No clients selected" : `${assignments.length} ${assignments.length === 1 ? "client" : "clients"} in the opening lineup`}</p>
      </div>

      {assignments.length === 0 ? (
        <div className="rounded-md border border-dashed border-line bg-white px-3 py-3 text-sm font-semibold text-muted">
          Click a client in the roster. One client is enough to start.
        </div>
      ) : (
        <div className="grid gap-1.5">
          {assignments.map((assignment, index) => {
            const options = clientProgramOptions.find((item) => item.client.id === assignment.client.id)?.programs ?? [];
            const selectionValue = selectedGroup
              ? programByClientId[assignment.client.id] ?? GROUP_TEMPLATE_VALUE
              : programByClientId[assignment.client.id] ?? assignment.program.id;
            return (
              <div
                className="grid grid-cols-[28px_34px_minmax(0,1fr)_auto] items-center gap-2 rounded-md border border-line bg-white px-2.5 py-1.5 shadow-[0_1px_2px_rgba(16,24,40,0.04)]"
                key={assignment.client.id}
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-panel text-xs font-bold text-muted">{index + 1}</span>
                <ClientAvatar name={assignment.client.name} size="sm" />
                <span className="min-w-0">
                  <span className="block truncate text-sm font-bold text-ink">{assignment.client.name}</span>
                  <select
                    aria-label={`Workout variant for ${assignment.client.name}`}
                    className="mt-1 w-full rounded-md border border-transparent bg-panel px-2 py-1 text-xs font-semibold text-muted transition hover:border-line hover:bg-white focus:border-brand focus:bg-white"
                    value={selectionValue}
                    onChange={(event) =>
                      onSelectProgram(
                        assignment.client.id,
                        event.target.value === GROUP_TEMPLATE_VALUE ? GROUP_TEMPLATE_VALUE : Number(event.target.value)
                      )
                    }
                  >
                    {selectedGroup ? <option value={GROUP_TEMPLATE_VALUE}>{selectedGroup.name} template</option> : null}
                    {options.map((program) => (
                      <option key={program.id} value={program.id}>
                        {programVariantName(assignment.client, program)}
                      </option>
                    ))}
                  </select>
                </span>
                <button
                  aria-label={`Remove ${assignment.client.name} from session`}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line text-muted transition hover:bg-panel hover:text-ink"
                  type="button"
                  onClick={() => onRemove(assignment.client.id)}
                >
                  <X size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function ClientPicker({
  clients,
  isLoading,
  maxClients,
  readinessByClientId,
  searchQuery,
  selectedCount,
  onAdd,
  onSearchChange,
  onSolo
}: {
  clients: ClientProgramOptions[];
  isLoading: boolean;
  maxClients: number;
  readinessByClientId: Record<number, ClientReadiness>;
  searchQuery: string;
  selectedCount: number;
  onAdd: (clientId: number) => void;
  onSearchChange: (query: string) => void;
  onSolo: (clientId: number) => void;
}) {
  const normalizedQuery = searchQuery.trim().toLowerCase();
  const filteredClients = normalizedQuery
    ? clients.filter(({ client }) =>
        [client.name, client.fitness_level, client.goals].some((value) => value.toLowerCase().includes(normalizedQuery))
      )
    : clients;
  const canAddMore = selectedCount < maxClients;

  return (
    <section className="flex min-h-0 flex-col overflow-hidden rounded-md border border-line bg-white p-2.5" id="clients" tabIndex={-1}>
      <div className="mb-2 flex shrink-0 flex-wrap items-start justify-between gap-2">
        <div>
          <p className="field-label">Client list</p>
          <p className="text-xs text-muted">{canAddMore ? `Choose up to ${maxClients} for this cockpit.` : "Cockpit is full. Remove someone to add another client."}</p>
        </div>
        <span className="rounded-full bg-panel px-2.5 py-1 text-xs font-bold text-muted">{clients.length} available</span>
      </div>
      {isLoading ? (
        <p className="text-sm text-muted">Loading clients and programs...</p>
      ) : (
        <>
          <label className="relative mb-1.5 block shrink-0">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={15} />
            <input
              aria-label="Search clients"
              className="field-control mt-0 pl-9"
              placeholder="Search client, level, goal"
              type="search"
              value={searchQuery}
              onChange={(event) => onSearchChange(event.target.value)}
            />
          </label>

          {filteredClients.length === 0 ? (
            <p className="rounded-md bg-panel px-3 py-2 text-sm text-muted">
              {clients.length === 0 ? "Every client with a program is already selected." : "No clients match this search."}
            </p>
          ) : (
            <div className="subtle-scrollbar grid min-h-0 flex-1 gap-1.5 overflow-y-auto pr-1">
              {filteredClients.map(({ client }) => {
                const readiness = readinessByClientId[client.id];
                return (
                  <button
                    aria-label={`Add ${client.name} to session`}
                    className="grid w-full grid-cols-[32px_minmax(0,1fr)_26px] items-center gap-2 rounded-md border border-line bg-white/75 px-2 py-1 text-left transition hover:border-brand/40 hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={!canAddMore}
                    key={client.id}
                    type="button"
                    onClick={() => (selectedCount === 0 ? onSolo(client.id) : onAdd(client.id))}
                  >
                    <ClientAvatar name={client.name} size="sm" />
                    <span className="min-w-0 flex-1">
                      <span className="flex min-w-0 items-center gap-1.5">
                        {readiness && <span aria-label={`Readiness ${readiness.readiness_status}`} className={readinessDotClassName(readiness.readiness_status)} />}
                        <span className="truncate text-sm font-bold text-ink">{client.name}</span>
                      </span>
                      <span className="block truncate text-xs text-muted">{clientListSubtext(client, readiness)}</span>
                    </span>
                    <span className="flex h-7 w-7 items-center justify-center rounded-md bg-brand/10 text-brand">
                      <UserPlus size={14} />
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </>
      )}
    </section>
  );
}

function ActiveSessionResume({ activeSession }: { activeSession: TrainingSession }) {
  return (
    <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2">
      <p className="text-sm font-semibold text-ink">Session #{activeSession.id} is active</p>
      <p className="text-xs text-muted">
        {activeSession.clients.length} {activeSession.clients.length === 1 ? "client" : "clients"} currently in the coach cockpit
      </p>
    </div>
  );
}

function FocusIcon({ focus }: { focus: SessionFocus }) {
  if (focus === "Conditioning Circuit") return <TimerReset size={15} />;
  if (focus === "Core Stability") return <ShieldCheck size={15} />;
  return <Dumbbell size={15} />;
}

function focusButtonClassName(focus: SessionFocus, isActive: boolean) {
  if (!isActive) return "bg-white text-muted hover:bg-panel hover:text-ink";
  if (focus === "Conditioning Circuit") return "bg-amber-50 text-ink shadow-[inset_0_0_0_1px_rgba(180,83,9,0.18)]";
  if (focus === "Core Stability") return "bg-emerald-50 text-ink shadow-[inset_0_0_0_1px_rgba(15,118,110,0.18)]";
  return "bg-blue-50 text-ink shadow-[inset_0_0_0_1px_rgba(36,84,214,0.16)]";
}

function clientListSubtext(client: ClientProgramOptions["client"], readiness: ClientReadiness | undefined) {
  if (!readiness) return `${client.fitness_level} - ${client.goals}`;
  if (!readiness.check_in) return `${client.fitness_level} - no check-in yet`;
  if (readiness.risk_flags.length > 0) return `${client.fitness_level} - ${readiness.risk_flags.join(", ")}`;
  return `${client.fitness_level} - ready`;
}

function readinessDotClassName(status: ClientReadiness["readiness_status"]) {
  const base = "h-2.5 w-2.5 shrink-0 rounded-full";
  if (status === "attention") return `${base} bg-danger`;
  if (status === "caution") return `${base} bg-warning`;
  if (status === "ready") return `${base} bg-success`;
  return `${base} bg-slate-300`;
}

function resolveAssignmentProgram(
  client: Client,
  programs: Program[],
  sessionFocus: SessionFocus,
  selectedGroup: TrainingGroup | null,
  overrideProgramId?: ProgramSelection
) {
  if (selectedGroup && (!overrideProgramId || overrideProgramId === GROUP_TEMPLATE_VALUE)) {
    return groupTemplateProgram(selectedGroup, client);
  }
  return resolveProgram(programs, sessionFocus, typeof overrideProgramId === "number" ? overrideProgramId : undefined);
}

function groupTemplateProgram(group: TrainingGroup, client: Client): Program {
  return {
    id: -group.id,
    client_id: client.id,
    name: `${client.name} - ${group.name}`,
    focus: group.focus,
    notes: group.notes,
    is_session_snapshot: true,
    created_at: group.created_at,
    exercises: group.exercises.map((item) => ({
      id: -item.id,
      order_index: item.order_index,
      sets: item.sets,
      reps: item.reps,
      weight_kg: item.weight_kg,
      rest_seconds: item.rest_seconds,
      notes: item.notes,
      exercise: item.exercise
    }))
  };
}

function isSessionFocus(value: string | null): value is SessionFocus {
  return SESSION_FOCI.some((item) => item.value === value);
}
