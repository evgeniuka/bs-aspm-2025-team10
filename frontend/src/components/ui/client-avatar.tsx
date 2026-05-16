import { clsx } from "clsx";

const THEMES = [
  { background: "#2454d6", foreground: "#ffffff" },
  { background: "#0f766e", foreground: "#ffffff" },
  { background: "#b45309", foreground: "#ffffff" },
  { background: "#be3f4f", foreground: "#ffffff" },
  { background: "#182033", foreground: "#ffffff" }
];

export function ClientAvatar({ className, name, size = "md" }: { className?: string; name: string; size?: "sm" | "md" | "lg" }) {
  const theme = THEMES[hashName(name) % THEMES.length];
  return (
    <span
      aria-hidden="true"
      className={clsx(
        "avatar-ring relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-md font-bold",
        size === "sm" && "h-8 w-8 text-[11px]",
        size === "md" && "h-9 w-9 text-xs",
        size === "lg" && "h-12 w-12 text-sm",
        className
      )}
      style={{ backgroundColor: theme.background, color: theme.foreground }}
    >
      <span className="absolute inset-x-0 top-0 h-1 bg-white/35" />
      <span className="absolute -bottom-2 -right-2 h-5 w-5 rounded-full bg-white/18" />
      <span className="relative">{initials(name)}</span>
    </span>
  );
}

function initials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2);
}

function hashName(name: string) {
  return [...name].reduce((sum, char) => sum + char.charCodeAt(0), 0);
}
