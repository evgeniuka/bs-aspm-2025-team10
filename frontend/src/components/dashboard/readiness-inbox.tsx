import { AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";
import type { ClientReadiness } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ClientAvatar } from "@/components/ui/client-avatar";

export function ReadinessInbox({ readiness }: { readiness: ClientReadiness[] }) {
  const sorted = [...readiness].sort((first, second) => statusRank(first.readiness_status) - statusRank(second.readiness_status));
  const visible = sorted.slice(0, 4);
  const submittedCount = readiness.filter((item) => item.check_in).length;

  return (
    <Card className="shrink-0 overflow-hidden border-brand/20">
      <CardHeader className="px-3 py-2.5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold text-ink">Readiness inbox</h2>
            <p className="text-xs text-muted">{submittedCount}/{readiness.length} checked in today</p>
          </div>
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-panel text-brand">
            <Clock3 size={16} />
          </span>
        </div>
      </CardHeader>
      <CardBody className="space-y-2 p-3">
        {visible.map((item) => (
          <a
            className="grid grid-cols-[32px_1fr_auto] items-center gap-2 rounded-md border border-line bg-white/80 px-2.5 py-2 transition hover:bg-panel"
            href={`#live-session`}
            key={item.client.id}
          >
            <ClientAvatar name={item.client.name} size="sm" />
            <span className="min-w-0">
              <span className="block truncate text-sm font-bold text-ink">{item.client.name}</span>
              <span className="block truncate text-xs text-muted">{readinessText(item)}</span>
            </span>
            <span className={readinessClassName(item.readiness_status)}>
              {readinessIcon(item.readiness_status)}
              {item.readiness_status}
            </span>
          </a>
        ))}
        {readiness.length === 0 && <p className="text-sm text-muted">No active clients yet.</p>}
      </CardBody>
    </Card>
  );
}

export function readinessClassName(status: ClientReadiness["readiness_status"]) {
  const base = "inline-flex min-h-7 items-center gap-1 rounded-full border px-2 text-[10px] font-bold uppercase";
  if (status === "attention") return `${base} border-red-200 bg-red-50 text-danger`;
  if (status === "caution") return `${base} border-amber-200 bg-amber-50 text-warning`;
  if (status === "ready") return `${base} border-emerald-200 bg-emerald-50 text-success`;
  return `${base} border-line bg-panel text-muted`;
}

function readinessIcon(status: ClientReadiness["readiness_status"]) {
  if (status === "attention") return <AlertTriangle size={12} />;
  if (status === "ready") return <CheckCircle2 size={12} />;
  return null;
}

function readinessText(item: ClientReadiness) {
  if (!item.check_in) return "No check-in yet";
  if (item.risk_flags.length > 0) return item.risk_flags.join(", ");
  return item.check_in.training_goal ?? "Ready to train";
}

function statusRank(status: ClientReadiness["readiness_status"]) {
  if (status === "attention") return 0;
  if (status === "caution") return 1;
  if (status === "missing") return 2;
  return 3;
}
