import type { Client } from "@/lib/types";
import { routes } from "@/lib/routes";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

export function ClientRoster({ clients }: { clients: Client[] }) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-ink">Client roster</h2>
          <p className="text-xs text-muted">Current active training clients</p>
        </div>
        <span className="status-pill">{clients.length} active</span>
      </CardHeader>
      <CardBody className="p-0">
        <div className="divide-y divide-line md:hidden">
          {clients.map((client) => (
            <a className="block px-4 py-3 transition hover:bg-panel" href={routes.client(client.id)} key={client.id}>
              <div className="flex items-start gap-3">
                <ClientAvatar name={client.name} />
                <span className="min-w-0 flex-1">
                  <span className="block font-semibold text-ink">{client.name}</span>
                  <span className="mt-1 inline-flex rounded-full border border-line bg-white px-2 py-1 text-xs font-semibold text-muted">
                    {client.fitness_level}
                  </span>
                  <span className="mt-2 block text-xs leading-5 text-muted">{client.goals}</span>
                </span>
                <span className="shrink-0 text-xs text-muted">Age {client.age}</span>
              </div>
            </a>
          ))}
        </div>
        <table className="hidden w-full table-fixed text-left text-sm md:table">
          <thead className="border-b border-line bg-panel/80 text-[11px] uppercase tracking-wide text-muted">
            <tr>
              <th className="w-[42%] px-4 py-2.5">Client</th>
              <th className="w-[22%] px-4 py-2.5">Level</th>
              <th className="px-4 py-2.5">Goal</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => (
              <tr className="border-b border-line transition hover:bg-panel last:border-0" key={client.id}>
                <td>
                  <a className="flex items-center gap-3 px-4 py-3 hover:text-brand" href={routes.client(client.id)}>
                    <ClientAvatar name={client.name} size="sm" />
                    <span>
                      <span className="block font-semibold text-ink">{client.name}</span>
                      <span className="text-xs text-muted">Age {client.age}</span>
                    </span>
                  </a>
                </td>
                <td className="text-muted">
                  <a className="block px-4 py-3" href={routes.client(client.id)}>
                    <span className="rounded-full border border-line bg-white px-2 py-1 text-xs font-semibold">{client.fitness_level}</span>
                  </a>
                </td>
                <td className="truncate text-muted">
                  <a className="block truncate px-4 py-3" href={routes.client(client.id)}>
                    {client.goals}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardBody>
    </Card>
  );
}
