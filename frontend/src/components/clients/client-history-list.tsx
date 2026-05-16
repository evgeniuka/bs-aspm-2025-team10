import type { ClientSessionSummary } from "@/lib/types";
import { formatDate, formatDuration } from "@/lib/format";
import { routes } from "@/lib/routes";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export function ClientHistoryList({
  sessionHref = routes.sessionSummary,
  sessions
}: {
  sessionHref?: (sessionId: number) => string;
  sessions: ClientSessionSummary[];
}) {
  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-bold text-ink">Workout history</h2>
      </CardHeader>
      <CardBody className="p-0">
        {sessions.length === 0 ? (
          <p className="p-4 text-sm text-muted">No sessions logged yet.</p>
        ) : (
          <div className="divide-y divide-line">
            {sessions.map((session) => (
              <a className="grid gap-3 px-4 py-3 transition hover:bg-panel md:grid-cols-[120px_1fr_100px_100px_100px]" href={sessionHref(session.session_id)} key={session.session_id}>
                <div>
                  <p className="text-sm font-bold text-ink">Session #{session.session_id}</p>
                  <p className="text-xs text-muted">{formatDate(session.ended_at ?? session.started_at)}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-ink">{session.program_name}</p>
                  <p className="truncate text-xs text-muted">{session.next_focus ?? session.coach_notes ?? "No coach note yet"}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase text-muted">Sets</p>
                  <p className="text-sm font-bold text-ink">
                    {session.sets_completed}/{session.planned_sets}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase text-muted">Volume</p>
                  <p className="text-sm font-bold text-ink">{session.volume_kg}kg</p>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase text-muted">Duration</p>
                  <p className="text-sm font-bold text-ink">{formatDuration(session.duration_minutes)}</p>
                </div>
              </a>
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
