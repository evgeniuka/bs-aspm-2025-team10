import type {
  Client,
  ClientCheckIn,
  ClientDetail,
  DashboardOverview,
  Exercise,
  Program,
  ProgramFocus,
  SessionSummary,
  TrainerAnalytics,
  TrainingGroup,
  TrainingSession,
  User
} from "./types";
import { request, type RequestOptions } from "@/lib/http";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api/v1";
const DEFAULT_WS_BASE = "ws://127.0.0.1:8000/api/v1";
const WS_BASE_ENV = process.env.NEXT_PUBLIC_WS_URL ?? DEFAULT_WS_BASE;

const apiRequest = <T>(path: string, options?: RequestOptions) => request<T>(API_BASE, path, options);

function resolveWsBase() {
  if (typeof window === "undefined") return trimTrailingSlash(WS_BASE_ENV);

  try {
    const url = new URL(WS_BASE_ENV);
    const browserHost = window.location.hostname;

    if (isLoopbackHost(url.hostname) && isLoopbackHost(browserHost)) {
      url.hostname = browserHost;
    }

    if (window.location.protocol === "https:" && url.protocol === "ws:") {
      url.protocol = "wss:";
    }

    return trimTrailingSlash(url.toString());
  } catch {
    return trimTrailingSlash(WS_BASE_ENV);
  }
}

function isLoopbackHost(hostname: string) {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
}

function trimTrailingSlash(value: string) {
  return value.replace(/\/$/, "");
}

export type CompleteSetPayload = {
  program_exercise_id?: number;
  exercise_id?: number;
  set_number?: number;
  reps_completed?: number;
  weight_kg?: number;
};

export type TrainingGroupPayload = {
  name: string;
  focus?: ProgramFocus | null;
  notes?: string | null;
  client_ids: number[];
  exercises: Array<{
    exercise_id: number;
    sets: number;
    reps: number;
    weight_kg: number;
    rest_seconds: number;
    notes?: string | null;
  }>;
};

export type TrainingGroupSessionPayload = {
  clients: Array<{
    client_id: number;
    program_id?: number | null;
  }>;
};

export type ClientPayload = {
  name: string;
  age: number;
  fitness_level: Client["fitness_level"];
  goals: string;
};

export const api = {
  wsUrl: (sessionId: number) => `${resolveWsBase()}/sessions/ws/${sessionId}`,
  login: (email: string, password: string) =>
    apiRequest<{ user: User }>("/auth/login", { method: "POST", json: { email, password } }),
  logout: () => apiRequest<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  me: () => apiRequest<User>("/auth/me"),
  dashboard: () => apiRequest<DashboardOverview>("/dashboard"),
  trainerAnalytics: () => apiRequest<TrainerAnalytics>("/analytics/trainer"),
  clients: () => apiRequest<Client[]>("/clients"),
  createClient: (payload: ClientPayload) => apiRequest<Client>("/clients", { method: "POST", json: payload }),
  updateClient: (clientId: number, payload: ClientPayload) => apiRequest<Client>(`/clients/${clientId}`, { method: "PATCH", json: payload }),
  archiveClient: (clientId: number) => apiRequest<void>(`/clients/${clientId}`, { method: "DELETE" }),
  clientDetail: (clientId: number) => apiRequest<ClientDetail>(`/clients/${clientId}`),
  traineeMe: () => apiRequest<ClientDetail>("/trainee/me"),
  upsertTraineeCheckIn: (payload: {
    energy_level: number;
    sleep_quality: number;
    soreness_level: number;
    pain_notes?: string | null;
    training_goal?: string | null;
  }) => apiRequest<ClientCheckIn>("/trainee/check-in/today", { method: "PUT", json: payload }),
  traineeProgram: (programId: number) => apiRequest<Program>(`/trainee/programs/${programId}`),
  traineeSessionSummary: (sessionId: number) => apiRequest<SessionSummary>(`/trainee/sessions/${sessionId}/summary`),
  exercises: () => apiRequest<Exercise[]>("/exercises"),
  groups: () => apiRequest<TrainingGroup[]>("/groups"),
  createGroup: (payload: TrainingGroupPayload) => apiRequest<TrainingGroup>("/groups", { method: "POST", json: payload }),
  updateGroup: (groupId: number, payload: TrainingGroupPayload) =>
    apiRequest<TrainingGroup>(`/groups/${groupId}`, { method: "PATCH", json: payload }),
  deleteGroup: (groupId: number) => apiRequest<void>(`/groups/${groupId}`, { method: "DELETE" }),
  startGroupSession: (groupId: number, payload?: TrainingGroupSessionPayload) =>
    apiRequest<{ session_id: number; session: TrainingSession }>(`/groups/${groupId}/sessions`, { method: "POST", json: payload }),
  programs: (clientId?: number) => apiRequest<Program[]>(clientId ? `/programs?client_id=${clientId}` : "/programs"),
  program: (programId: number) => apiRequest<Program>(`/programs/${programId}`),
  createProgram: (payload: {
    client_id: number;
    name: string;
    focus?: ProgramFocus | null;
    notes?: string;
    exercises: Array<{
      exercise_id: number;
      sets: number;
      reps: number;
      weight_kg: number;
      rest_seconds: number;
    }>;
  }) => apiRequest<Program>("/programs", { method: "POST", json: payload }),
  updateProgram: (
    programId: number,
    payload: {
      name: string;
      focus?: ProgramFocus | null;
      notes?: string | null;
      exercises: Array<{
        exercise_id: number;
        sets: number;
        reps: number;
        weight_kg: number;
        rest_seconds: number;
        notes?: string | null;
      }>;
    }
  ) => apiRequest<Program>(`/programs/${programId}`, { method: "PATCH", json: payload }),
  startSession: (payload: { client_ids: number[]; program_ids: number[] }) =>
    apiRequest<{ session_id: number; session: TrainingSession }>("/sessions", { method: "POST", json: payload }),
  session: (sessionId: number) => apiRequest<TrainingSession>(`/sessions/${sessionId}`),
  completeSet: (sessionId: number, clientId: number, payload?: CompleteSetPayload) =>
    apiRequest<TrainingSession>(`/sessions/${sessionId}/clients/${clientId}/complete-set`, { method: "POST", json: payload }),
  undoLastSet: (sessionId: number, clientId: number) =>
    apiRequest<TrainingSession>(`/sessions/${sessionId}/clients/${clientId}/undo-last-set`, { method: "POST" }),
  startNextSet: (sessionId: number, clientId: number) =>
    apiRequest<TrainingSession>(`/sessions/${sessionId}/clients/${clientId}/start-next-set`, { method: "POST" }),
  endSession: (sessionId: number) => apiRequest<TrainingSession>(`/sessions/${sessionId}/end`, { method: "POST" }),
  sessionSummary: (sessionId: number) => apiRequest<SessionSummary>(`/sessions/${sessionId}/summary`),
  updateSessionClientSummary: (
    sessionId: number,
    clientId: number,
    payload: { coach_notes?: string | null; next_focus?: string | null }
  ) => apiRequest<SessionSummary>(`/sessions/${sessionId}/clients/${clientId}/summary`, { method: "PATCH", json: payload })
};
