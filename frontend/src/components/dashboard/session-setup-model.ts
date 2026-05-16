import type { Client, Program, ProgramFocus, TrainingSession } from "@/lib/types";

export type ClientProgramOptions = {
  client: Client;
  programs: Program[];
};

export type SessionAssignment = {
  client: Client;
  program: Program;
};

export type SessionFocus = ProgramFocus;

export const SESSION_FOCI: Array<{
  description: string;
  label: string;
  value: SessionFocus;
}> = [
  { description: "Main lifts", label: "Strength", value: "Strength Block" },
  { description: "Higher tempo", label: "Conditioning", value: "Conditioning Circuit" },
  { description: "Control work", label: "Core Stability", value: "Core Stability" }
];

export const DEFAULT_SESSION_FOCUS: SessionFocus = "Strength Block";
export const MAX_COCKPIT_CLIENTS = 10;

const PREFERRED_PROGRAM_ORDER: ProgramFocus[] = ["Strength Block", "Conditioning Circuit", "Core Stability"];

export function buildClientProgramOptions(clients: Client[], programs: Program[]) {
  const programsByClient = new Map<number, Program[]>();
  for (const program of programs) {
    const clientPrograms = programsByClient.get(program.client_id) ?? [];
    clientPrograms.push(program);
    programsByClient.set(program.client_id, clientPrograms);
  }

  return clients
    .map((client) => ({
      client,
      programs: [...(programsByClient.get(client.id) ?? [])].sort(compareProgramVariants)
    }))
    .filter((item): item is ClientProgramOptions => item.programs.length > 0);
}

export function buildSessionPayload(assignments: SessionAssignment[]) {
  const selected = assignments.slice(0, MAX_COCKPIT_CLIENTS);
  return {
    client_ids: selected.map((item) => item.client.id),
    program_ids: selected.map((item) => item.program.id)
  };
}

export function plannedProgramStats(program: Program) {
  return program.exercises.reduce(
    (stats, exercise) => ({
      sets: stats.sets + exercise.sets,
      volumeKg: stats.volumeKg + exercise.sets * exercise.reps * exercise.weight_kg
    }),
    { sets: 0, volumeKg: 0 }
  );
}

export function ctaLabel({
  activeSession,
  isPending,
  isPreparing,
  selectedCount
}: {
  activeSession: TrainingSession | null;
  isPending: boolean;
  isPreparing: boolean;
  selectedCount: number;
}) {
  if (isPreparing) return "Preparing...";
  if (isPending) return "Starting...";
  if (activeSession) return "Resume realtime cockpit";
  if (selectedCount === 0) return "Choose clients first";
  return selectedCount === 1 ? "Start solo training" : `Start ${selectedCount}-client training`;
}

export function resolveProgram(programs: Program[], sessionFocus: SessionFocus, overrideProgramId?: number) {
  return programs.find((program) => program.id === overrideProgramId) ?? programs.find((program) => program.focus === sessionFocus) ?? programs[0];
}

export function programVariantName(client: Client, program: Program) {
  if (program.focus) return program.focus;
  const firstNamePrefix = `${client.name.split(" ")[0]} `;
  return program.name.startsWith(firstNamePrefix) ? program.name.slice(firstNamePrefix.length) : program.name;
}

export function clientInitials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2);
}

function compareProgramVariants(left: Program, right: Program) {
  return programRank(left) - programRank(right) || left.name.localeCompare(right.name);
}

function programRank(program: Program) {
  if (!program.focus) return PREFERRED_PROGRAM_ORDER.length;
  const index = PREFERRED_PROGRAM_ORDER.indexOf(program.focus);
  return index === -1 ? PREFERRED_PROGRAM_ORDER.length : index;
}
