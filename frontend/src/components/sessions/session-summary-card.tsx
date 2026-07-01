"use client";

import { Save } from "lucide-react";
import { useState } from "react";
import type { SessionClientSummary } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

export type SessionSummaryNotes = { coach_notes: string | null; next_focus: string | null };

export function SessionSummaryCard({
  client,
  readOnly = false,
  isSaving = false,
  clientHref,
  onSave
}: {
  client: SessionClientSummary;
  readOnly?: boolean;
  isSaving?: boolean;
  clientHref?: string;
  onSave?: (payload: SessionSummaryNotes) => void;
}) {
  const [coachNotes, setCoachNotes] = useState(client.coach_notes ?? "");
  const [nextFocus, setNextFocus] = useState(client.next_focus ?? "");

  const completion = client.planned_sets > 0 ? Math.min(100, Math.round((client.sets_completed / client.planned_sets) * 100)) : 0;

  function save() {
    onSave?.({
      coach_notes: coachNotes.trim() || null,
      next_focus: nextFocus.trim() || null
    });
  }

  return (
    <Card data-testid={`session-summary-card-${client.client_id}`}>
      <CardHeader className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <ClientAvatar name={client.client_name} />
          <div className="min-w-0">
            {clientHref ? (
              <a className="truncate text-lg font-bold text-ink underline-offset-2 hover:underline" href={clientHref}>
                {client.client_name}
              </a>
            ) : (
              <h3 className="truncate text-lg font-bold text-ink">{client.client_name}</h3>
            )}
            <p className="truncate text-sm text-muted">{client.program_name}</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <span className="status-pill">
            {client.sets_completed}/{client.planned_sets} sets
          </span>
          <span className="status-pill">{client.volume_kg}kg</span>
          <span className="status-pill">{completion}%</span>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        <div className="space-y-2">
          {client.exercises.map((exercise) => (
            <div className="rounded-md border border-line bg-white/80 px-3 py-2" key={exercise.exercise_id}>
              <div className="flex items-center justify-between gap-3">
                <p className="truncate text-sm font-semibold text-ink">{exercise.exercise_name}</p>
                <p className="shrink-0 text-xs font-semibold text-muted">
                  {exercise.sets_completed}/{exercise.planned_sets} sets - {exercise.volume_kg}kg
                </p>
              </div>
              {exercise.sets.length > 0 ? (
                <ul className="mt-1.5 space-y-0.5">
                  {exercise.sets.map((set) => (
                    <li className="text-xs text-muted" key={`${set.program_exercise_id ?? exercise.exercise_id}-${set.set_number}`}>
                      Set {set.set_number}: {set.reps_completed} reps x {set.weight_kg}kg = {set.volume_kg}kg
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-1.5 text-xs text-muted">No sets logged.</p>
              )}
            </div>
          ))}
          {client.exercises.length === 0 && <p className="text-sm text-muted">No exercises logged for this client.</p>}
        </div>

        {readOnly ? (
          <div className="space-y-2">
            <CoachNote label="Coach notes" value={client.coach_notes ?? "No coach note for this session."} />
            <CoachNote label="Next focus" value={client.next_focus ?? "No next focus set yet."} />
          </div>
        ) : (
          <div className="space-y-3">
            <label className="block">
              <span className="field-label">Coach notes</span>
              <textarea
                aria-label={`Coach notes for ${client.client_name}`}
                className="field-control min-h-20 resize-none"
                maxLength={1000}
                value={coachNotes}
                onChange={(event) => setCoachNotes(event.target.value)}
              />
            </label>
            <label className="block">
              <span className="field-label">Next focus</span>
              <input
                aria-label={`Next focus for ${client.client_name}`}
                className="field-control"
                maxLength={180}
                value={nextFocus}
                onChange={(event) => setNextFocus(event.target.value)}
              />
            </label>
            <Button className="w-full" disabled={isSaving} onClick={save}>
              <Save size={16} />
              {isSaving ? "Saving..." : "Save"}
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
}

function CoachNote({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <p className="field-label">{label}</p>
      <p className="mt-1 text-sm font-semibold leading-6 text-ink">{value}</p>
    </div>
  );
}
