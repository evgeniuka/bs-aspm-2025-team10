"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ClientAnalytics, ClientVolumePoint } from "@/lib/types";
import { formatDate } from "@/lib/format";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export function ClientAnalyticsChart({ analytics, points }: { analytics?: ClientAnalytics; points?: ClientVolumePoint[] }) {
  const chartPoints = points ?? analytics?.volume_by_session ?? [];
  const exerciseBreakdown = analytics?.exercise_breakdown ?? [];
  const data = chartPoints.map((point) => ({
    session: `#${point.session_id}`,
    date: formatDate(point.date),
    volume: point.volume_kg,
    sets: point.sets_completed
  }));

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-ink">Volume trend</h2>
            <p className="text-xs text-muted">Actual logs across completed sessions</p>
          </div>
          {analytics ? <span className="status-pill">{analytics.completion_rate}% completion</span> : null}
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        {analytics ? (
          <div className="grid gap-2 sm:grid-cols-3">
            <MiniMetric label="Avg volume" value={`${analytics.average_volume_kg}kg`} />
            <MiniMetric label="Best session" value={`${analytics.best_volume_kg}kg`} />
            <MiniMetric label="Sets" value={`${analytics.total_sets}/${analytics.planned_sets}`} />
          </div>
        ) : null}

        {data.length === 0 ? (
          <div className="flex h-64 items-center justify-center rounded-md border border-dashed border-line bg-panel text-sm font-semibold text-muted">
            No completed workout volume yet
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={data}>
                <CartesianGrid stroke="#d9e0ea" vertical={false} />
                <XAxis dataKey="session" tickLine={false} />
                <YAxis tickLine={false} width={48} />
                <Tooltip
                  cursor={false}
                  contentStyle={{ borderColor: "#d9e0ea", borderRadius: 8 }}
                  formatter={(value, name) => [`${value}kg`, name === "volume" ? "Volume" : name]}
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.date ?? ""}
                />
                <Bar barSize={48} dataKey="volume" fill="#2563eb" minPointSize={4} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {exerciseBreakdown.length > 0 ? (
          <div className="overflow-hidden rounded-md border border-line">
            <div className="grid grid-cols-[1fr_72px_86px] bg-panel px-3 py-2 text-xs font-bold uppercase text-muted">
              <span>Exercise</span>
              <span className="text-right">Sets</span>
              <span className="text-right">Volume</span>
            </div>
            {exerciseBreakdown.slice(0, 5).map((exercise) => (
              <div className="grid grid-cols-[1fr_72px_86px] border-t border-line px-3 py-2 text-sm" key={exercise.exercise_id}>
                <span className="font-semibold text-ink">{exercise.exercise_name}</span>
                <span className="text-right text-muted">{exercise.sets_completed}</span>
                <span className="text-right font-semibold text-ink">{exercise.volume_kg}kg</span>
              </div>
            ))}
          </div>
        ) : null}
      </CardBody>
    </Card>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <p className="text-[10px] font-bold uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1 text-base font-bold text-ink">{value}</p>
    </div>
  );
}
