"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle2, StopCircle, Users } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, type CompleteSetPayload } from "@/lib/api";
import { ApiError, getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { RealtimeEvent, TrainingSession } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { CockpitQuadrant } from "@/components/cockpit/cockpit-quadrant";

export function CockpitGrid({ sessionId }: { sessionId: number }) {
  const queryClient = useQueryClient();
  const [liveSession, setLiveSession] = useState<TrainingSession | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<"connecting" | "live" | "reconnecting">("connecting");
  const { data: fetchedSession, isLoading } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => api.session(sessionId)
  });
  const session = liveSession ?? fetchedSession;
  const lastRevisionRef = useRef(-1);
  const applySession = useCallback(
    (next: TrainingSession) => {
      // Ignore stale/out-of-order payloads (WS echo vs HTTP response race): server revision
      // only ever increases, so never let an older snapshot clobber a newer one.
      if (next.revision < lastRevisionRef.current) return;
      lastRevisionRef.current = next.revision;
      setLiveSession(next);
      queryClient.setQueryData(["session", sessionId], next);
    },
    [queryClient, sessionId]
  );

  useEffect(() => {
    let socket: WebSocket | null = null;
    let retryId: number | undefined;
    let closedByEffect = false;

    function connect() {
      setConnectionState((current) => (current === "connecting" ? "connecting" : "reconnecting"));
      socket = new WebSocket(api.wsUrl(sessionId));
      socket.onopen = () => setConnectionState("live");
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as RealtimeEvent;
          applySession(payload.session);
          setActionError(null);
        } catch {
          setActionError("Realtime update could not be read. Session state was refreshed.");
          void queryClient.invalidateQueries({ queryKey: ["session", sessionId] });
        }
      };
      socket.onerror = () => setConnectionState("reconnecting");
      socket.onclose = () => {
        if (closedByEffect) return;
        setConnectionState("reconnecting");
        void queryClient.invalidateQueries({ queryKey: ["session", sessionId] });
        retryId = window.setTimeout(connect, 1500);
      };
    }

    connect();
    return () => {
      closedByEffect = true;
      if (retryId) window.clearTimeout(retryId);
      socket?.close();
    };
  }, [applySession, queryClient, sessionId]);

  const complete = useMutation({
    mutationFn: ({ clientId, payload }: { clientId: number; payload: Required<CompleteSetPayload> }) =>
      api.completeSet(sessionId, clientId, payload),
    onSuccess: (data) => {
      setActionError(null);
      applySession(data);
    },
    onError: (error) => {
      if (error instanceof ApiError && error.status === 409) {
        setActionError("Session changed. The latest state was refreshed.");
        setLiveSession(null);
        void queryClient.invalidateQueries({ queryKey: ["session", sessionId] });
        return;
      }
      setActionError(getErrorMessage(error));
    }
  });
  const start = useMutation({
    mutationFn: (clientId: number) => api.startNextSet(sessionId, clientId),
    onSuccess: (data) => {
      setActionError(null);
      applySession(data);
    },
    onError: (error) => setActionError(getErrorMessage(error))
  });
  const undo = useMutation({
    mutationFn: (clientId: number) => api.undoLastSet(sessionId, clientId),
    onSuccess: (data) => {
      setActionError(null);
      applySession(data);
    },
    onError: (error) => setActionError(getErrorMessage(error))
  });
  const end = useMutation({
    mutationFn: () => api.endSession(sessionId),
    onSuccess: (data) => {
      applySession(data);
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setIsRedirecting(true);
      window.setTimeout(() => window.location.assign(routes.sessionSummary(sessionId)), 700);
    }
  });

  if (isLoading || !session) {
    return <div className="p-6 text-sm text-muted">Loading live session...</div>;
  }

  const isCompleted = session.status === "completed";
  const isEnding = end.isPending || isRedirecting;

  return (
    <div className="min-h-screen">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-white px-6 py-4">
        <div>
          <p className="field-label">Live cockpit</p>
          <h1 className="text-xl font-semibold text-ink">Session #{session.id}</h1>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <span className="status-pill">
            <Users size={13} />
            {session.clients.length} {session.clients.length === 1 ? "client" : "clients"}
          </span>
          <span className={connectionPillClassName(connectionState)} data-testid="connection-state">
            {connectionState}
          </span>
          <span className="status-pill capitalize">{isEnding ? "saving" : session.status}</span>
          {isCompleted ? (
            <a
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-line bg-white px-4 py-2 text-sm font-medium text-ink transition hover:bg-panel"
              href={routes.dashboard}
            >
              <ArrowLeft size={16} />
              Back to dashboard
            </a>
          ) : (
            <>
              <a
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-line bg-white px-4 py-2 text-sm font-medium text-ink transition hover:bg-panel"
                href={routes.dashboard}
              >
                <ArrowLeft size={16} />
                Dashboard
              </a>
              <Button disabled={isEnding} variant="danger" onClick={() => end.mutate()}>
                <StopCircle size={16} />
                {isEnding ? "Ending..." : "End session"}
              </Button>
            </>
          )}
        </div>
      </header>
      {isCompleted && (
        <div className="border-b border-line bg-success-soft px-6 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="text-success" size={20} />
              <div>
                <p className="font-medium text-ink">Session completed</p>
                <p className="text-sm text-muted">Workout history is saved. Opening the session summary...</p>
              </div>
            </div>
            <a
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
              href={routes.dashboard}
            >
              <ArrowLeft size={16} />
              Back to dashboard
            </a>
          </div>
        </div>
      )}
      {end.error && <p className="border-b border-line bg-danger-soft px-6 py-3 text-sm font-medium text-danger">{getErrorMessage(end.error)}</p>}
      {connectionState !== "live" && (
        <p className="border-b border-line bg-brand-soft px-6 py-3 text-sm font-medium text-brand">
          Reconnecting realtime channel. Controls still use the latest saved session state.
        </p>
      )}
      {actionError && <p className="border-b border-line bg-warning-soft px-6 py-3 text-sm font-medium text-warning">{actionError}</p>}
      <section className="grid min-h-[calc(100vh-81px)] grid-cols-1 gap-3 p-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {session.clients.map((participant) => (
          <CockpitQuadrant
            disabled={complete.isPending || start.isPending || undo.isPending || isCompleted}
            key={`${participant.client_id}-${participant.status}-${participant.rest_time_remaining}-${participant.current_exercise_index}-${participant.current_set}`}
            participant={participant}
            onCompleteSet={(clientId, payload) => complete.mutate({ clientId, payload })}
            onStartNextSet={(clientId) => start.mutate(clientId)}
            onUndoLastSet={(clientId) => undo.mutate(clientId)}
          />
        ))}
      </section>
    </div>
  );
}

function connectionPillClassName(state: "connecting" | "live" | "reconnecting") {
  const base = "status-pill capitalize";
  if (state === "live") return `${base} border-success-soft bg-success-soft text-success`;
  if (state === "reconnecting") return `${base} border-warning-soft bg-warning-soft text-warning`;
  return base;
}
