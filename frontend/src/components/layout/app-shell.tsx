"use client";

import { BarChart3, LayoutDashboard, Layers3, LogOut, Play, Users } from "lucide-react";
import type { ReactNode } from "react";
import { useMutation } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { routes } from "@/lib/routes";
import { Button } from "@/components/ui/button";
import { BrandMark } from "@/components/ui/brand-mark";

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const logout = useMutation({
    mutationFn: api.logout,
    onSettled: () => window.location.assign(routes.login)
  });
  const navItems = [
    { href: routes.dashboard, icon: <LayoutDashboard size={18} />, label: "Home", active: pathname === routes.dashboard },
    { href: routes.clients, icon: <Users size={18} />, label: "Clients", active: pathname.startsWith("/clients") },
    { href: routes.groups, icon: <Layers3 size={18} />, label: "Groups", active: pathname.startsWith("/groups") },
    { href: routes.analytics, icon: <BarChart3 size={18} />, label: "Analytics", active: pathname.startsWith(routes.analytics) }
  ];

  return (
    <div className="min-h-screen">
      <header className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-line bg-white px-3 lg:hidden">
        <a className="flex items-center gap-2" href={routes.dashboard}>
          <BrandMark />
          <span className="text-sm font-semibold text-ink">FitCoach Pro</span>
        </a>
        <Button aria-label="Sign out" size="sm" variant="secondary" onClick={() => logout.mutate()}>
          <LogOut size={15} />
        </Button>
      </header>

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col border-r border-line bg-white px-4 py-5 lg:flex">
        <a className="flex items-center gap-2.5 px-1" href={routes.dashboard}>
          <BrandMark />
          <span className="text-base font-semibold text-ink">FitCoach Pro</span>
        </a>

        <a
          className="mt-6 inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-brand px-4 text-sm font-medium text-white transition hover:bg-blue-700"
          href={routes.newSession}
        >
          <Play size={16} />
          Start session
        </a>

        <nav className="mt-5 space-y-1">
          {navItems.map((item) => (
            <a
              className={`flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition ${
                item.active ? "bg-brand-soft text-brand" : "text-muted hover:bg-panel hover:text-ink"
              }`}
              aria-current={item.active ? "page" : undefined}
              href={item.href}
              key={item.label}
            >
              {item.icon}
              <span>{item.label}</span>
            </a>
          ))}
        </nav>

        <Button aria-label="Sign out" className="mt-auto justify-start" variant="ghost" onClick={() => logout.mutate()}>
          <LogOut size={16} />
          <span>Sign out</span>
        </Button>
      </aside>

      <nav className="fixed inset-x-3 bottom-3 z-40 grid grid-cols-4 gap-1 rounded-2xl border border-line bg-white p-1 shadow-elevated lg:hidden">
        {navItems.map((item) => (
          <a
            className={`flex min-h-12 flex-col items-center justify-center gap-0.5 rounded-xl text-[11px] font-medium transition ${
              item.active ? "bg-brand-soft text-brand" : "text-muted hover:bg-panel hover:text-ink"
            }`}
            aria-current={item.active ? "page" : undefined}
            href={item.href}
            key={item.label}
          >
            {item.icon}
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <main className="min-h-screen pb-24 pt-14 lg:pb-0 lg:pl-60 lg:pt-0">{children}</main>
    </div>
  );
}
