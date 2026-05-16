import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClientHistoryList } from "./client-history-list";
import type { ClientSessionSummary } from "@/lib/types";

const sessions: ClientSessionSummary[] = [
  {
    session_id: 4,
    status: "completed",
    started_at: "2026-05-11T10:00:00Z",
    ended_at: "2026-05-11T10:45:00Z",
    duration_minutes: 45,
    program_name: "Strength Block",
    sets_completed: 4,
    planned_sets: 6,
    volume_kg: 720,
    coach_notes: "Better control",
    next_focus: "Tempo squats"
  }
];

describe("ClientHistoryList", () => {
  it("links each session back to its summary", () => {
    render(<ClientHistoryList sessions={sessions} />);

    expect(screen.getByText("Workout history")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /session #4/i })).toHaveAttribute("href", "/sessions/4/summary");
    expect(screen.getByText("Tempo squats")).toBeInTheDocument();
  });
});
