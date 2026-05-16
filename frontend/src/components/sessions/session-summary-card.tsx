"use client";

import { Save } from "lucide-react";
import { useState } from "react";
import { routes } from "@/lib/routes";
import type { SessionClientSummary } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

export function SessionSummaryCard({
  client,
  isSaving = false,
  readOnly = false,
  onSave
}: {
  client: SessionClientSummary;
  isSaving?: boolean;
  readOnly?: boolean;
  onSave: (clientId: number, payload: { coach_notes: string | null; next_focus: string | null }) => void;
}) {
  const [coachNotes, setCoachNotes] = useState(client.coach_notes ?? "");
  const [nextFocus, setNextFocus] = useState(client.next_focus ?? "");
  const completion = client.planned_sets > 0 ? Math.round((client.sets_completed / client.planned_sets) * 100) : 0;

  function handleSave() {
    onSave(client.client_id, {
      coach_notes: coachNotes.trim() || null,
      next_focus: nextFocus.trim() || null
    });
  }

  return (
    <Card data-testid={`session-summary-card-${client.client_id}`}>
      <CardHeader className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <ClientAvatar name={client.client_name} />
          <div className="min-w-0">
            <a className="block truncate text-base font-bold text-ink hover:text-brand" href={routes.client(client.client_id)}>
              {client.client_name}
            </a>
            <p className="truncate text-sm text-muted">{client.program_name}</p>
          </div>
        </div>
        <span className="rounded-full border border-line bg-white px-3 py-1 text-xs font-bold uppercase text-muted">{completion}% complete</span>
      </CardHeader>
      <CardBody className="space-y-4">
        <div className="meter-track">
          <div className="meter-fill" style={{ width: `${completion}%` }} />
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <Metric label="Sets" value={`${client.sets_completed}/${client.planned_sets}`} />
          <Metric label="Actual volume" value={`${client.volume_kg}kg`} />
          <Metric label="Status" value={client.status} />
        </div>

        <div className="rounded-md border border-line">
          {client.exercises.map((exercise, index) => (
            <div className="border-b border-line px-3 py-2 text-sm last:border-0" key={`${exercise.exercise_id}-${index}`}>
              <div className="grid grid-cols-[1fr_84px_110px] items-center gap-3">
                <span className="truncate font-semibold text-ink">{exercise.exercise_name}</span>
                <span className="text-right text-muted">
                  {exercise.sets_completed}/{exercise.planned_sets} sets
                </span>
                <span className="text-right text-muted">{exercise.volume_kg}kg actual</span>
              </div>
              {exercise.sets.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {exercise.sets.map((set) => (
                    <span className="rounded-full bg-panel px-2 py-1 text-xs font-semibold text-muted" key={`${set.exercise_id}-${set.set_number}-${set.created_at}`}>
                      Set {set.set_number}: {set.reps_completed} reps x {set.weight_kg}kg = {set.volume_kg}kg
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {readOnly ? (
          <div className="grid gap-3 md:grid-cols-2">
            <ReadOnlyNote label="Coach notes" value={client.coach_notes ?? "No coach note yet"} />
            <ReadOnlyNote label="Next focus" value={client.next_focus ?? "No next focus set"} />
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
            <label className="block">
              <span className="field-label">Coach notes</span>
              <textarea
                aria-label={`Coach notes for ${client.client_name}`}
                className="field-control min-h-20 resize-y"
                value={coachNotes}
                onChange={(event) => setCoachNotes(event.target.value)}
              />
            </label>
            <label className="block">
              <span className="field-label">Next focus</span>
              <input
                aria-label={`Next focus for ${client.client_name}`}
                className="field-control"
                value={nextFocus}
                onChange={(event) => setNextFocus(event.target.value)}
              />
            </label>
            <div className="flex items-end">
              <Button className="w-full" disabled={isSaving} variant="secondary" onClick={handleSave}>
                <Save size={16} />
                {isSaving ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}

function ReadOnlyNote({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <p className="field-label">{label}</p>
      <p className="mt-1 text-sm font-semibold text-ink">{value}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <p className="text-xs font-semibold uppercase text-muted">{label}</p>
      <p className="mt-1 text-lg font-bold text-ink">{value}</p>
    </div>
  );
}
