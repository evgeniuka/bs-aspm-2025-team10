import { Card, CardBody } from "@/components/ui/card";

export function MetricCard({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <Card className="overflow-hidden">
      <CardBody className="relative">
        <div className="absolute inset-x-0 top-0 h-1 bg-brand" />
        <p className="text-xs font-bold uppercase tracking-wide text-muted">{label}</p>
        <div className="mt-3">
          <p className="text-3xl font-bold leading-none text-ink">{value}</p>
        </div>
        <p className="mt-2 text-xs leading-5 text-muted">{detail}</p>
      </CardBody>
    </Card>
  );
}
