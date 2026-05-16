"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Edit3, ExternalLink, Plus, Save, Search, X } from "lucide-react";
import type { Dispatch, SetStateAction } from "react";
import { useMemo, useState } from "react";
import { api, type ClientPayload } from "@/lib/api";
import { getErrorMessage } from "@/lib/http";
import { routes } from "@/lib/routes";
import type { Client } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

type FormState = ClientPayload & {
  id?: number;
};

const EMPTY_FORM: FormState = {
  name: "",
  age: 30,
  fitness_level: "Beginner",
  goals: ""
};
const EMPTY_CLIENTS: Client[] = [];

export function ClientManagementView() {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const clientsQuery = useQuery({ queryKey: ["clients"], queryFn: api.clients, retry: false });
  const clients = clientsQuery.data ?? EMPTY_CLIENTS;
  const filteredClients = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return clients;
    return clients.filter((client) =>
      [client.name, client.fitness_level, client.goals].some((value) => value.toLowerCase().includes(normalized))
    );
  }, [clients, query]);

  const save = useMutation({
    mutationFn: (payload: FormState) =>
      payload.id ? api.updateClient(payload.id, formToPayload(payload)) : api.createClient(formToPayload(payload)),
    onSuccess: () => {
      setForm(EMPTY_FORM);
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    }
  });

  const archive = useMutation({
    mutationFn: api.archiveClient,
    onSuccess: () => {
      setForm(EMPTY_FORM);
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    }
  });

  function editClient(client: Client) {
    setForm({
      id: client.id,
      name: client.name,
      age: client.age,
      fitness_level: client.fitness_level,
      goals: client.goals
    });
  }

  function archiveClient(client: Client) {
    if (window.confirm(`Archive ${client.name}? Existing history stays available in completed sessions.`)) {
      archive.mutate(client.id);
    }
  }

  const canSave = form.name.trim().length >= 2 && form.goals.trim().length >= 8 && form.age >= 13 && form.age <= 100;
  const error = clientsQuery.error ?? save.error ?? archive.error;

  return (
    <div className="page-wrap">
      <header className="page-titlebar visual-card flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-muted">Roster management</p>
          <h1 className="text-3xl font-bold text-ink">Clients</h1>
          <p className="mt-1 max-w-3xl text-sm text-muted">Create profiles, keep goals current, and archive inactive clients without touching session history.</p>
        </div>
        <Button variant="secondary" onClick={() => setForm(EMPTY_FORM)}>
          <Plus size={16} />
          New client
        </Button>
      </header>

      {error ? <p className="rounded-md bg-red-50 p-3 text-sm font-semibold text-danger">{getErrorMessage(error)}</p> : null}

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
        <Card className="overflow-hidden">
          <CardHeader className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-ink">Active roster</h2>
              <p className="text-xs text-muted">{clients.length} clients available for sessions and groups</p>
            </div>
            <label className="relative block w-full sm:w-72">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={15} />
              <input
                aria-label="Search clients"
                className="field-control mt-0 pl-9"
                placeholder="Search name, level, goal"
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
          </CardHeader>
          <CardBody className="p-0">
            {clientsQuery.isLoading ? <p className="p-4 text-sm text-muted">Loading clients...</p> : null}
            {filteredClients.length === 0 && !clientsQuery.isLoading ? <p className="p-4 text-sm text-muted">No clients match this search.</p> : null}
            <div className="divide-y divide-line">
              {filteredClients.map((client) => (
                <article className="grid gap-3 px-4 py-3 transition hover:bg-panel/60 min-[760px]:grid-cols-[minmax(0,1fr)_140px_160px]" key={client.id}>
                  <div className="flex min-w-0 items-start gap-3">
                    <ClientAvatar name={client.name} size="md" />
                    <div className="min-w-0">
                      <a className="truncate text-base font-bold text-ink hover:text-brand" href={routes.client(client.id)}>
                        {client.name}
                      </a>
                      <p className="mt-1 line-clamp-2 text-sm text-muted">{client.goals}</p>
                    </div>
                  </div>
                  <div className="text-sm">
                    <p className="field-label">Level</p>
                    <p className="font-bold text-ink">{client.fitness_level}</p>
                    <p className="text-xs text-muted">{client.age} years</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 min-[760px]:justify-end">
                    <a
                      className="inline-flex min-h-9 items-center justify-center gap-1.5 rounded-md border border-line bg-white px-3 text-xs font-bold text-ink transition hover:bg-panel"
                      href={routes.client(client.id)}
                    >
                      Profile
                      <ExternalLink size={13} />
                    </a>
                    <Button size="sm" variant="secondary" onClick={() => editClient(client)}>
                      <Edit3 size={13} />
                      Edit
                    </Button>
                    <Button aria-label={`Archive ${client.name}`} size="sm" variant="ghost" onClick={() => archiveClient(client)}>
                      <Archive size={13} />
                    </Button>
                  </div>
                </article>
              ))}
            </div>
          </CardBody>
        </Card>

        <ClientForm form={form} isSaving={save.isPending} canSave={canSave} onCancel={() => setForm(EMPTY_FORM)} onChange={setForm} onSave={() => save.mutate(form)} />
      </section>
    </div>
  );
}

function ClientForm({
  canSave,
  form,
  isSaving,
  onCancel,
  onChange,
  onSave
}: {
  canSave: boolean;
  form: FormState;
  isSaving: boolean;
  onCancel: () => void;
  onChange: Dispatch<SetStateAction<FormState>>;
  onSave: () => void;
}) {
  const mode = form.id ? "Edit client" : "New client";
  const patchForm = (patch: Partial<FormState>) => onChange((current) => ({ ...current, ...patch }));

  return (
    <Card className="h-fit overflow-hidden">
      <CardHeader className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-ink">{mode}</h2>
          <p className="text-xs text-muted">Used in roster, groups, sessions, and profile history.</p>
        </div>
        {form.id ? (
          <Button aria-label="Cancel edit" size="sm" variant="ghost" onClick={onCancel}>
            <X size={14} />
          </Button>
        ) : null}
      </CardHeader>
      <CardBody className="space-y-3">
        <label className="block" htmlFor="client-name">
          <span className="field-label">Name</span>
          <input id="client-name" className="field-control" value={form.name} onChange={(event) => patchForm({ name: event.target.value })} />
        </label>
        <div className="grid grid-cols-[100px_1fr] gap-3">
          <label className="block" htmlFor="client-age">
            <span className="field-label">Age</span>
            <input
              id="client-age"
              className="field-control"
              min={13}
              max={100}
              type="number"
              value={form.age}
              onChange={(event) => patchForm({ age: Number(event.target.value) || 0 })}
            />
          </label>
          <label className="block" htmlFor="client-fitness-level">
            <span className="field-label">Fitness level</span>
            <select
              id="client-fitness-level"
              className="field-control"
              value={form.fitness_level}
              onChange={(event) => patchForm({ fitness_level: event.target.value as Client["fitness_level"] })}
            >
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </label>
        </div>
        <label className="block" htmlFor="client-goals">
          <span className="field-label">Training goals</span>
          <textarea
            id="client-goals"
            className="field-control min-h-28 resize-none"
            value={form.goals}
            onChange={(event) => patchForm({ goals: event.target.value })}
          />
        </label>
        <Button className="w-full" disabled={!canSave || isSaving} onClick={onSave}>
          <Save size={16} />
          {isSaving ? "Saving..." : form.id ? "Save client" : "Create client"}
        </Button>
        {!canSave ? <p className="rounded-md bg-amber-50 p-2 text-xs font-semibold text-warning">Name, age, and a clear goal are required.</p> : null}
      </CardBody>
    </Card>
  );
}

function formToPayload(form: FormState): ClientPayload {
  return {
    name: form.name.trim(),
    age: form.age,
    fitness_level: form.fitness_level,
    goals: form.goals.trim()
  };
}
