"use client";

import { Activity, BarChart3, ShieldCheck, Users } from "lucide-react";
import type { ReactNode } from "react";
import Image from "next/image";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { routes } from "@/lib/routes";
import { Button } from "@/components/ui/button";
import { Card, CardBody } from "@/components/ui/card";
import { BrandMark } from "@/components/ui/brand-mark";

const DEMO_ACCOUNTS = {
  trainer: {
    email: "trainer@fitcoach.dev",
    password: "demo-password",
    label: "Trainer demo"
  },
  trainee: {
    email: "maya@fitcoach.dev",
    password: "demo-password",
    label: "Client demo"
  }
} as const;

export default function LoginPage() {
  const [selectedDemo, setSelectedDemo] = useState<keyof typeof DEMO_ACCOUNTS>("trainer");
  const [email, setEmail] = useState<string>(DEMO_ACCOUNTS.trainer.email);
  const [password, setPassword] = useState<string>(DEMO_ACCOUNTS.trainer.password);

  const login = useMutation({
    mutationFn: () => api.login(email, password),
    onSuccess: ({ user }) => window.location.assign(user.role === "trainee" ? routes.clientPortal : routes.dashboard)
  });

  function handleLogin() {
    login.mutate();
  }

  function selectDemo(kind: keyof typeof DEMO_ACCOUNTS) {
    const account = DEMO_ACCOUNTS[kind];
    setSelectedDemo(kind);
    setEmail(account.email);
    setPassword(account.password);
    login.reset();
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4 sm:p-6">
      <div className="grid w-full max-w-[1040px] overflow-hidden rounded-xl border border-white/70 bg-white/80 shadow-elevated backdrop-blur lg:grid-cols-[0.95fr_1.05fr]">
        <section className="p-5 sm:p-8">
          <div className="mb-6 flex items-center gap-3">
            <BrandMark size="lg" />
            <div>
              <h1 className="text-2xl font-bold text-ink">FitCoach Pro 2.0</h1>
              <p className="text-sm text-muted">Trainer operations workspace</p>
            </div>
          </div>
          <Card className="border-line/80">
            <CardBody className="space-y-5">
              <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-ink">
                  <ShieldCheck className="text-success" size={17} />
                  Demo account
                </div>
                <p className="mt-1 text-xs text-muted">Trainer and client sides use safe seeded data.</p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(DEMO_ACCOUNTS).map(([kind, account]) => (
                  <button
                    aria-pressed={selectedDemo === kind}
                    className={`rounded-md border px-3 py-2 text-left text-sm font-bold transition ${
                      selectedDemo === kind ? "border-brand bg-blue-50 text-ink" : "border-line bg-white text-muted hover:bg-panel hover:text-ink"
                    }`}
                    key={kind}
                    type="button"
                    onClick={() => selectDemo(kind as keyof typeof DEMO_ACCOUNTS)}
                  >
                    {account.label}
                  </button>
                ))}
              </div>
              <div className="space-y-4">
                <label className="block">
                  <span className="field-label">Email</span>
                  <input
                    className="field-control"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    type="email"
                  />
                </label>
                <label className="block">
                  <span className="field-label">Password</span>
                  <input
                    className="field-control"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    type="password"
                  />
                </label>
                {login.error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">Login failed. Check that the API is running and seeded.</p>}
                <Button className="w-full" disabled={login.isPending} type="button" onClick={handleLogin}>
                  {login.isPending ? "Signing in..." : "Sign in to demo"}
                </Button>
              </div>
            </CardBody>
          </Card>
        </section>

        <section className="visual-card hidden min-h-[560px] border-0 bg-mist p-7 lg:block">
          <div className="flex h-full flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold text-ink">
                <Activity className="text-brand" size={18} />
                Realtime coach cockpit
              </div>
              <p className="mt-2 max-w-md text-sm leading-6 text-muted">
                A compact workspace for roster selection, live set logging, summaries, and client history.
              </p>
            </div>
            <Image alt="" className="mx-auto my-8 w-full max-w-[520px]" height={520} priority src="/visuals/coach-workspace.svg" width={720} />
            <div className="grid grid-cols-3 gap-3">
              <VisualMetric icon={<Users size={17} />} label="Roster" value="1-10" />
              <VisualMetric icon={<Activity size={17} />} label="Logging" value="Live" />
              <VisualMetric icon={<BarChart3 size={17} />} label="History" value="Actual" />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function VisualMetric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="surface-panel p-3">
      <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-panel text-brand">{icon}</span>
      <p className="mt-3 text-lg font-bold leading-none text-ink">{value}</p>
      <p className="mt-1 text-[11px] font-bold uppercase tracking-wide text-muted">{label}</p>
    </div>
  );
}
