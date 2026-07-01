export function formatDuration(minutes: number) {
  const safe = Number.isFinite(minutes) && minutes > 0 ? Math.round(minutes) : 0;
  if (safe < 60) {
    return `${safe}m`;
  }
  return `${Math.floor(safe / 60)}h ${safe % 60}m`;
}

export function formatTimer(seconds: number) {
  const safe = Number.isFinite(seconds) && seconds > 0 ? Math.round(seconds) : 0;
  const minutes = Math.floor(safe / 60);
  const remainder = safe % 60;
  return `${minutes}:${String(remainder).padStart(2, "0")}`;
}

export function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric"
  }).format(date);
}
