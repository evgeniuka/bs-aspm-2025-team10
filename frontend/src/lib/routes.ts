export const routes = {
  login: "/login",
  dashboard: "/dashboard",
  clients: "/clients",
  groups: "/groups",
  analytics: "/analytics",
  clientPortal: "/client",
  newSession: "/sessions/new",
  newProgram: "/programs/new",
  program: (programId: number) => `/programs/${programId}`,
  session: (sessionId: number) => `/sessions/${sessionId}`,
  sessionSummary: (sessionId: number) => `/sessions/${sessionId}/summary`,
  clientSessionSummary: (sessionId: number) => `/client/sessions/${sessionId}`,
  client: (clientId: number) => `/clients/${clientId}`
};
