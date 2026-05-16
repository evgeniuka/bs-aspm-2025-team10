"use client";

import { Activity, BarChart3, ClipboardList, Layers3, LayoutDashboard, LogOut, Users } from "lucide-react";
import type { MouseEvent, ReactNode } from "react";
import { useMutation } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import Image from "next/image";
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
    { href: routes.dashboard, icon: <LayoutDashboard size={18} />, label: "Dashboard", active: pathname === routes.dashboard },
    {
      href: routes.clients,
      icon: <Users size={18} />,
      label: "Clients",
      active: pathname.startsWith("/clients")
    },
    {
      href: `${routes.dashboard}#programs`,
      icon: <ClipboardList size={18} />,
      label: "Programs",
      active: pathname.startsWith("/programs")
    },
    {
      href: routes.groups,
      icon: <Layers3 size={18} />,
      label: "Groups",
      active: pathname.startsWith("/groups")
    },
    { href: `${routes.dashboard}#live-session`, icon: <Activity size={18} />, label: "Session setup", active: pathname.startsWith("/sessions") },
    { href: routes.analytics, icon: <BarChart3 size={18} />, label: "Analytics", active: pathname.startsWith(routes.analytics) }
  ];

  function handleNavClick(event: MouseEvent<HTMLAnchorElement>, href: string) {
    if (!href.startsWith(`${routes.dashboard}#`) || pathname !== routes.dashboard) return;
    const targetId = href.split("#")[1];
    const target = document.getElementById(targetId);
    if (!target) return;
    event.preventDefault();
    window.history.replaceState(null, "", href);
    target.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
    target.focus({ preventScroll: true });
  }

  return (
    <div className="min-h-screen">
      <header className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-white/70 bg-white/95 px-3 shadow-[0_1px_16px_rgba(16,24,40,0.06)] backdrop-blur lg:hidden">
        <a className="flex items-center gap-2" href={routes.dashboard}>
          <BrandMark />
          <span className="text-sm font-bold text-ink">FitCoach Pro</span>
        </a>
        <Button aria-label="Sign out" size="sm" variant="secondary" onClick={() => logout.mutate()}>
          <LogOut size={15} />
        </Button>
      </header>

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-white/70 bg-white/90 px-4 py-5 shadow-[4px_0_28px_rgba(16,24,40,0.06)] backdrop-blur lg:flex">
        <div className="visual-card flex items-center justify-center gap-3 px-2 py-2 lg:justify-start lg:px-3 lg:py-3">
          <BrandMark />
          <div className="hidden lg:block">
            <p className="text-xs font-bold uppercase tracking-wide text-muted">FitCoach</p>
            <h1 className="text-base font-bold text-ink">Pro 2.0</h1>
          </div>
        </div>
        <nav className="mt-6 space-y-1">
          <p className="hidden px-3 pb-2 text-[11px] font-bold uppercase tracking-wide text-muted lg:block">Workspace</p>
          {navItems.map((item) => (
            <a
              aria-label={item.label}
              className={`flex min-h-10 items-center justify-start gap-3 rounded-md px-3 text-sm font-semibold transition ${
                item.active ? "bg-ink text-white" : "text-muted hover:bg-panel hover:text-ink"
              }`}
              href={item.href}
              key={item.label}
              onClick={(event) => handleNavClick(event, item.href)}
            >
              {item.icon}
              <span>{item.label}</span>
            </a>
          ))}
        </nav>
        <div className="absolute bottom-20 left-4 right-4 overflow-hidden rounded-lg border border-line bg-panel p-3">
          <Image alt="" className="mb-3 h-20 w-full rounded-md object-cover" height={220} loading="eager" src="/visuals/session-grid.svg" width={360} />
          <p className="text-xs font-bold uppercase tracking-wide text-muted">Demo system</p>
          <p className="mt-1 text-sm font-semibold text-ink">Local API + realtime cockpit</p>
          <div className="mt-3 flex items-center gap-2 text-xs text-muted">
            <span className="h-2 w-2 rounded-full bg-success shadow-[0_0_0_3px_rgba(21,128,61,0.12)]" />
            Running on 127.0.0.1
          </div>
        </div>
        <Button
          aria-label="Sign out"
          className="absolute bottom-4 left-2 right-2 px-0 lg:bottom-5 lg:left-4 lg:right-4 lg:px-3"
          variant="secondary"
          onClick={() => logout.mutate()}
        >
          <LogOut size={16} />
          <span className="hidden lg:inline">Sign out</span>
        </Button>
      </aside>

      <nav className="fixed inset-x-2 bottom-2 z-40 grid grid-cols-5 gap-1 rounded-lg border border-white/80 bg-white/95 p-1 shadow-elevated backdrop-blur lg:hidden">
        {navItems
          .filter((item) => item.label !== "Programs")
          .map((item) => (
            <a
              aria-label={item.label}
              className={`flex min-h-12 flex-col items-center justify-center gap-0.5 rounded-md text-[10px] font-bold transition ${
                item.active ? "bg-ink text-white" : "text-muted hover:bg-panel hover:text-ink"
              }`}
              href={item.href}
              key={item.label}
              onClick={(event) => handleNavClick(event, item.href)}
            >
              {item.icon}
              <span>{item.label === "Session setup" ? "Session" : item.label}</span>
            </a>
          ))}
      </nav>

      <main className="min-h-screen pb-20 pt-14 lg:pb-0 lg:pl-64 lg:pt-0">{children}</main>
    </div>
  );
}
