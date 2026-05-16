import { Dumbbell } from "lucide-react";
import { clsx } from "clsx";

export function BrandMark({ className, size = "md" }: { className?: string; size?: "sm" | "md" | "lg" }) {
  return (
    <span
      aria-hidden="true"
      className={clsx(
        "relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-md bg-ink text-white shadow-[0_8px_20px_rgba(17,24,39,0.18)]",
        size === "sm" && "h-9 w-9",
        size === "md" && "h-10 w-10",
        size === "lg" && "h-12 w-12",
        className
      )}
    >
      <span className="absolute inset-x-0 top-0 h-1 bg-teal" />
      <span className="absolute bottom-0 right-0 h-5 w-5 rounded-tl-full bg-gold/90" />
      <Dumbbell size={size === "lg" ? 24 : 20} />
    </span>
  );
}
