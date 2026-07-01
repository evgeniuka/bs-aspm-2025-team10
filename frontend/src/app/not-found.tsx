import { routes } from "@/lib/routes";
import { BrandMark } from "@/components/ui/brand-mark";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center">
      <BrandMark />
      <p className="field-label">404</p>
      <h1 className="text-2xl font-bold text-ink">Page not found</h1>
      <p className="max-w-md text-sm text-muted">The page you are looking for does not exist or may have moved.</p>
      <a
        className="inline-flex min-h-10 items-center justify-center rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
        href={routes.dashboard}
      >
        Back to dashboard
      </a>
    </main>
  );
}
