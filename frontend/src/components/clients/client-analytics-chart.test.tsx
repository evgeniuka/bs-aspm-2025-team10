import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClientAnalyticsChart } from "./client-analytics-chart";

describe("ClientAnalyticsChart", () => {
  it("renders an empty state before the client has completed volume", () => {
    render(<ClientAnalyticsChart points={[]} />);

    expect(screen.getByText("No completed workout volume yet")).toBeInTheDocument();
  });

  it("renders richer client analytics when the full analytics object is provided", () => {
    render(
      <ClientAnalyticsChart
        analytics={{
          total_sessions: 2,
          completed_sessions: 2,
          total_sets: 10,
          planned_sets: 12,
          total_volume_kg: 900,
          average_volume_kg: 450,
          best_volume_kg: 520,
          completion_rate: 83,
          average_session_minutes: 44,
          volume_by_session: [],
          exercise_breakdown: [{ exercise_id: 1, exercise_name: "Goblet Squat", sets_completed: 4, volume_kg: 360, last_logged_at: null }]
        }}
      />
    );

    expect(screen.getByText("83% completion")).toBeInTheDocument();
    expect(screen.getByText("Goblet Squat")).toBeInTheDocument();
  });
});
