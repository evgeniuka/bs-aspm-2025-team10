"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Check, Play, Plus, Users } from "lucide-react";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { Client, ClientReadiness, Program, TrainingGroup } from "@/lib/types";
import {
  buildClientProgramOptions,
  buildSessionPayload,
  DEFAULT_SESSION_FOCUS,
  MAX_COCKPIT_CLIENTS,
  programVariantName,
  resolveProgram,
  type SessionAssignment
} from "@/components/dashboard/session-setup-model";
import { Button } from "@/components/ui/button";
import { ClientAvatar } from "@/components/ui/client-avatar";

const GROUP_TEMPLATE = "group" as const;
type ProgramChoice = number | typeof GROUP_TEMPLATE;
const STEPS = ["Choose clients", "Assign programs", "Review and start"] as const;

export function SessionWizard() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [groupId, setGroupId] = useState<number | null>(null);
  const [programByClient, setProgramByClient] = useState<Record<number, ProgramChoice>>({});

  const clientsQuery = useQuery({ queryKey: ["clients"], queryFn: api.clients, retry: false });
  const programsQuery = useQuery({ queryKey: ["programs"], queryFn: () => api.programs(), retry: false });
  const groupsQuery = useQuery({ queryKey: ["groups"], queryFn: api.groups, retry: false });
  const dashboardQuery = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard, retry: false });

  const options = useMemo(
    () => buildClientProgramOptions(clientsQuery.data ?? [], programsQuery.data ?? []),
    [clientsQuery.data, programsQuery.data]
  );
  const programsByClient = useMemo<Record<number, Program[]>>(
    () => Object.fromEntries(options.map((option) => [option.client.id, option.programs])),
    [options]
  );
  const groups = useMemo(() => groupsQuery.data ?? [], [groupsQuery.data]);
  const group = groupId ? groups.find((item) => item.id === groupId) ?? null : null;
  const readinessById = useMemo<Record<number, ClientReadiness>>(
    () => Object.fromEntries((dashboardQuery.data?.today_readiness ?? []).map((item) => [item.client.id, item])),
    [dashboardQuery.data]
  );

  const rosterClients: Client[] = group ? group.clients : options.map((option) => option.client);
  const selectedClients = rosterClients.filter((client) => selectedIds.includes(client.id));
  const isLoading = clientsQuery.isLoading || programsQuery.isLoading || groupsQuery.isLoading;

  function toggleClient(clientId: number) {
    setSelectedIds((current) => {
      if (current.includes(clientId)) return current.filter((id) => id !== clientId);
      if (current.length >= MAX_COCKPIT_CLIENTS) return current;
      return [...current, clientId];
    });
  }

  function pickGroup(id: number) {
    const next = groups.find((item) => item.id === id);
    if (!next) return;
    setGroupId(id);
    setSelectedIds(next.clients.map((client) => client.id).slice(0, MAX_COCKPIT_CLIENTS));
    setProgramByClient({});
  }

  function clearGroup() {
    setGroupId(null);
    setSelectedIds([]);
    setProgramByClient({});
  }

  function programChoiceFor(clientId: number): ProgramChoice {
    const choice = programByClient[clientId];
    if (choice !== undefined) return choice;
    if (group) return GROUP_TEMPLATE;
    const resolved = resolveProgram(programsByClient[clientId] ?? [], DEFAULT_SESSION_FOCUS);
    return resolved ? resolved.id : GROUP_TEMPLATE;
  }

  function programLabelFor(clientId: number): string {
    const choice = programChoiceFor(clientId);
    if (choice === GROUP_TEMPLATE) return group ? `${group.name} template` : "Coach's pick";
    const program = (programsByClient[clientId] ?? []).find((item) => item.id === choice);
    const client = rosterClients.find((item) => item.id === clientId);
    return program && client ? programVariantName(client, program) : "Coach's pick";
  }

  const start = useMutation({
    mutationFn: () => {
      if (group) {
        return api.startGroupSession(group.id, {
          clients: selectedIds.map((id) => {
            const choice = programChoiceFor(id);
            return { client_id: id, program_id: typeof choice === "number" ? choice : null };
          })
        });
      }
      const assignments: SessionAssignment[] = selectedClients
        .map((client) => {
          const choice = programChoiceFor(client.id);
          const program = resolveProgram(
            programsByClient[client.id] ?? [],
            DEFAULT_SESSION_FOCUS,
            typeof choice === "number" ? choice : undefined
          );
          return program ? { client, program } : null;
        })
        .filter((item): item is SessionAssignment => Boolean(item));
      return api.startSession(buildSessionPayload(assignments));
    },
    onSuccess: (data) => router.push(routes.session(data.session_id))
  });

  const canContinue = selectedIds.length >= 1 && selectedIds.length <= MAX_COCKPIT_CLIENTS;

  return (
    <div className="mx-auto max-w-[760px] px-4 py-8 sm:px-6">
      <div className="visual-card overflow-hidden">
        <WizardHeader step={step} onBack={() => (step === 0 ? router.push(routes.dashboard) : setStep(step - 1))} />

        <div className="p-5">
          {isLoading ? (
            <p className="py-10 text-center text-sm text-muted">Loading your roster...</p>
          ) : step === 0 ? (
            <ChooseClients
              group={group}
              groups={groups}
              readinessById={readinessById}
              rosterClients={rosterClients}
              selectedIds={selectedIds}
              onClearGroup={clearGroup}
              onPickGroup={pickGroup}
              onToggle={toggleClient}
            />
          ) : step === 1 ? (
            <AssignPrograms
              group={group}
              programChoiceFor={programChoiceFor}
              programsByClient={programsByClient}
              selectedClients={selectedClients}
              onSelect={(clientId, choice) => setProgramByClient((current) => ({ ...current, [clientId]: choice }))}
            />
          ) : (
            <ReviewStart programLabelFor={programLabelFor} selectedClients={selectedClients} />
          )}
        </div>

        <WizardFooter
          canContinue={canContinue}
          error={start.error ? getErrorMessage(start.error) : null}
          isStarting={start.isPending}
          selectedCount={selectedIds.length}
          step={step}
          onBack={() => setStep(step - 1)}
          onNext={() => setStep(step + 1)}
          onStart={() => start.mutate()}
        />
      </div>
    </div>
  );
}

function WizardHeader({ step, onBack }: { step: number; onBack: () => void }) {
  return (
    <div className="border-b border-line px-5 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <button
            aria-label="Back"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted transition hover:bg-panel hover:text-ink"
            type="button"
            onClick={onBack}
          >
            <ArrowLeft size={16} />
          </button>
          <h1 className="text-lg font-semibold text-ink">Start a session</h1>
        </div>
        <span className="text-xs text-muted">
          Step {step + 1} of {STEPS.length}
        </span>
      </div>
      <div className="mt-3.5 flex gap-1.5">
        {STEPS.map((label, index) => (
          <span
            className={`h-1.5 flex-1 rounded-full ${index <= step ? "bg-brand" : "bg-line"}`}
            key={label}
          />
        ))}
      </div>
      <p className="mt-3 text-sm">
        <span className="font-medium text-ink">{STEPS[step]}</span>
        {step === 0 ? <span className="text-muted"> · pick 1 to 10 for the cockpit</span> : null}
      </p>
    </div>
  );
}

function ChooseClients({
  group,
  groups,
  readinessById,
  rosterClients,
  selectedIds,
  onClearGroup,
  onPickGroup,
  onToggle
}: {
  group: TrainingGroup | null;
  groups: TrainingGroup[];
  readinessById: Record<number, ClientReadiness>;
  rosterClients: Client[];
  selectedIds: number[];
  onClearGroup: () => void;
  onPickGroup: (id: number) => void;
  onToggle: (clientId: number) => void;
}) {
  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex items-center justify-between">
          <p className="field-label">Quick start from a saved group</p>
          {group ? (
            <button className="text-xs font-medium text-brand" type="button" onClick={onClearGroup}>
              Clear group
            </button>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          {groups.length === 0 ? <p className="text-sm text-muted">No saved groups yet.</p> : null}
          {groups.map((item) => {
            const active = group?.id === item.id;
            return (
              <button
                className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                  active ? "border-brand bg-brand-soft text-brand" : "border-line bg-white text-ink hover:bg-panel"
                }`}
                key={item.id}
                type="button"
                onClick={() => onPickGroup(item.id)}
              >
                {item.name} · {item.clients.length}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <p className="field-label mb-1">{group ? "Confirm attendance" : "Roster"}</p>
        <div>
          {rosterClients.length === 0 ? (
            <p className="rounded-md border border-dashed border-line bg-white px-3 py-3 text-sm text-muted">
              No clients yet — add a client on the Clients page, then start a session.
            </p>
          ) : null}
          {rosterClients.map((client) => {
            const selected = selectedIds.includes(client.id);
            const readiness = readinessById[client.id];
            return (
              <button
                aria-label={`${selected ? "Remove" : "Select"} ${client.name}`}
                aria-pressed={selected}
                className="flex w-full items-center gap-3 border-b border-line py-2.5 text-left last:border-b-0"
                key={client.id}
                type="button"
                onClick={() => onToggle(client.id)}
              >
                <ClientAvatar name={client.name} size="sm" />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium text-ink">{client.name}</span>
                  <span className="block truncate text-xs text-muted">{clientSubtext(client, readiness)}</span>
                </span>
                {readiness ? <ReadinessPill status={readiness.readiness_status} /> : null}
                <span
                  className={`flex h-6 w-6 items-center justify-center rounded-full ${
                    selected ? "bg-brand text-white" : "border border-line text-muted"
                  }`}
                >
                  {selected ? <Check size={14} /> : <Plus size={14} />}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function AssignPrograms({
  group,
  programChoiceFor,
  programsByClient,
  selectedClients,
  onSelect
}: {
  group: TrainingGroup | null;
  programChoiceFor: (clientId: number) => ProgramChoice;
  programsByClient: Record<number, Program[]>;
  selectedClients: Client[];
  onSelect: (clientId: number, choice: ProgramChoice) => void;
}) {
  return (
    <div className="space-y-1">
      <p className="mb-3 text-sm text-muted">
        {group ? "Each client uses the group template unless you pick a saved plan." : "Each client trains their matching plan — change it if today calls for something else."}
      </p>
      {selectedClients.map((client) => {
        const programs = programsByClient[client.id] ?? [];
        const choice = programChoiceFor(client.id);
        return (
          <div className="flex items-center gap-3 border-b border-line py-3 last:border-b-0" key={client.id}>
            <ClientAvatar name={client.name} size="sm" />
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{client.name}</span>
            <select
              aria-label={`Workout for ${client.name}`}
              className="h-9 max-w-[200px] rounded-lg border border-line bg-white px-2.5 text-sm text-ink transition hover:border-slate-300 focus:border-brand"
              value={String(choice)}
              onChange={(event) => onSelect(client.id, event.target.value === GROUP_TEMPLATE ? GROUP_TEMPLATE : Number(event.target.value))}
            >
              {group ? <option value={GROUP_TEMPLATE}>{group.name} template</option> : null}
              {programs.map((program) => (
                <option key={program.id} value={program.id}>
                  {programVariantName(client, program)}
                </option>
              ))}
            </select>
          </div>
        );
      })}
    </div>
  );
}

function ReviewStart({
  programLabelFor,
  selectedClients
}: {
  programLabelFor: (clientId: number) => string;
  selectedClients: Client[];
}) {
  return (
    <div>
      <div className="mb-4 flex items-center gap-2 text-sm text-muted">
        <Users size={16} />
        {selectedClients.length} {selectedClients.length === 1 ? "client" : "clients"} ready for the cockpit
      </div>
      <div>
        {selectedClients.map((client) => (
          <div className="flex items-center gap-3 border-b border-line py-2.5 last:border-b-0" key={client.id}>
            <ClientAvatar name={client.name} size="sm" />
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{client.name}</span>
            <span className="truncate text-sm text-muted">{programLabelFor(client.id)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function WizardFooter({
  canContinue,
  error,
  isStarting,
  selectedCount,
  step,
  onBack,
  onNext,
  onStart
}: {
  canContinue: boolean;
  error: string | null;
  isStarting: boolean;
  selectedCount: number;
  step: number;
  onBack: () => void;
  onNext: () => void;
  onStart: () => void;
}) {
  return (
    <div className="space-y-3 border-t border-line bg-panel px-5 py-4">
      {error ? <p className="rounded-lg bg-danger-soft px-3 py-2 text-sm text-danger">{error}</p> : null}
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted">
          <span className="font-medium text-ink">{selectedCount} selected</span> · up to {MAX_COCKPIT_CLIENTS}
        </span>
        <div className="flex gap-2">
          {step > 0 ? (
            <Button variant="secondary" onClick={onBack}>
              Back
            </Button>
          ) : null}
          {step < STEPS.length - 1 ? (
            <Button disabled={!canContinue} onClick={onNext}>
              Next
              <ArrowRight size={16} />
            </Button>
          ) : (
            <Button disabled={!canContinue || isStarting} onClick={onStart}>
              <Play size={16} />
              {isStarting ? "Starting..." : "Start session"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

function ReadinessPill({ status }: { status: ClientReadiness["readiness_status"] }) {
  const map = {
    ready: { label: "Ready", className: "bg-success-soft text-success" },
    caution: { label: "Caution", className: "bg-warning-soft text-warning" },
    attention: { label: "Attention", className: "bg-danger-soft text-danger" },
    missing: { label: "No check-in", className: "bg-panel text-muted" }
  } as const;
  const entry = map[status] ?? map.missing;
  return <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${entry.className}`}>{entry.label}</span>;
}

function clientSubtext(client: Client, readiness: ClientReadiness | undefined) {
  if (!readiness || !readiness.check_in) return client.fitness_level;
  if (readiness.risk_flags.length > 0) return `${client.fitness_level} · ${readiness.risk_flags.join(", ")}`;
  return client.fitness_level;
}
