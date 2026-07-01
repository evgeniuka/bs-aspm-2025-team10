"use client";

import { Button } from "@/components/ui/button";
import { routes } from "@/lib/routes";

export default function ErrorBoundary({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center">
      <p className="field-label">Something went wrong</p>
      <h1 className="text-2xl font-bold text-ink">This screen hit an unexpected error</h1>
      <p className="max-w-md text-sm text-muted">{error.message || "Please try again."}</p>
      <div className="flex flex-wrap items-center justify-center gap-2">
        <Button onClick={reset}>Try again</Button>
        <a
          className="inline-flex min-h-10 items-center justify-center rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-panel"
          href={routes.dashboard}
        >
          Back to dashboard
        </a>
      </div>
    </main>
  );
}
