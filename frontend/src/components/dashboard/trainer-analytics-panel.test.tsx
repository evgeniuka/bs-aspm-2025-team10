import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrainerAnalyticsCard } from "./trainer-analytics-panel";
import type { TrainerAnalytics } from "@/lib/types";

const analytics: TrainerAnalytics = {
  total_sessions: 3,
  completed_sessions: 2,
  active_sessions: 1,
  total_sets_completed: 14,
  total_planned_sets: 20,
  total_volume_kg: 1240,
  completion_rate: 70,
  average_sets_per_session: 7,
  average_session_minutes: 42,
  volume_by_day: [{ date: "2026-05-12", volume_kg: 1240, sets_completed: 14 }],
  weekly_volume: [{ week_start: "2026-05-11", volume_kg: 1240, sets_completed: 14, sessions: 2 }],
  focus_mix: [
    {
      focus: "Strength Block",
      client_sessions: 2,
      sets_completed: 14,
      planned_sets: 20,
      volume_kg: 1240,
      completion_rate: 70
    }
  ],
  top_exercises: [{ exercise_id: 1, exercise_name: "Goblet Squat", sets_completed: 6, volume_kg: 600, clients: 2 }],
  readiness_mix: [
    { status: "ready", clients: 1 },
    { status: "caution", clients: 0 },
    { status: "attention", clients: 0 },
    { status: "missing", clients: 0 }
  ],
  attention_clients: [
    {
      client_id: 7,
      client_name: "Maya Levi",
      readiness_status: "ready",
      risk_flags: ["low completion"],
      completion_rate: 70,
      last_workout_date: "2026-05-12T10:00:00Z",
      days_since_last_workout: 1
    }
  ],
  client_load: [
    {
      client_id: 7,
      client_name: "Maya Levi",
      sessions: 3,
      sets_completed: 8,
      planned_sets: 10,
      volume_kg: 720,
      completion_rate: 80,
      last_workout_date: "2026-05-12T10:00:00Z"
    }
  ]
};

describe("TrainerAnalyticsCard", () => {
  it("renders aggregate trainer metrics and client load links", () => {
    render(<TrainerAnalyticsCard analytics={analytics} />);

    expect(screen.getByText("Trainer analytics")).toBeInTheDocument();
    expect(screen.getAllByText("1240kg").length).toBeGreaterThan(0);
    expect(screen.getByText("14/20")).toBeInTheDocument();
    expect(screen.getByText("Focus mix")).toBeInTheDocument();
    expect(screen.getByText("Top exercises")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /maya levi/i })[0]).toHaveAttribute("href", "/clients/7");
  });
});
