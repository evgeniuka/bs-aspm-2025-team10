import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SessionSummaryCard } from "./session-summary-card";
import type { SessionClientSummary } from "@/lib/types";

const client: SessionClientSummary = {
  session_client_id: 1,
  client_id: 10,
  client_name: "Maya Levi",
  program_id: 2,
  program_name: "Maya Strength Block",
  status: "completed",
  sets_completed: 2,
  planned_sets: 6,
  volume_kg: 320,
  coach_notes: "Good tempo",
  next_focus: "Squat depth",
  exercises: [
    {
      exercise_id: 1,
      exercise_name: "Goblet Squat",
      sets_completed: 2,
      planned_sets: 3,
      reps_completed: 16,
      volume_kg: 320,
      sets: [
        {
          program_exercise_id: 1,
          exercise_id: 1,
          exercise_name: "Goblet Squat",
          set_number: 1,
          reps_completed: 8,
          weight_kg: 20,
          volume_kg: 160,
          created_at: new Date().toISOString()
        },
        {
          program_exercise_id: 1,
          exercise_id: 1,
          exercise_name: "Goblet Squat",
          set_number: 2,
          reps_completed: 8,
          weight_kg: 20,
          volume_kg: 160,
          created_at: new Date().toISOString()
        }
      ]
    }
  ]
};

describe("SessionSummaryCard", () => {
  it("renders summary metrics and saves notes", () => {
    const onSave = vi.fn();
    render(<SessionSummaryCard client={client} onSave={onSave} />);

    expect(screen.getByText("Maya Levi")).toBeInTheDocument();
    expect(screen.getByText("2/6")).toBeInTheDocument();
    expect(screen.getAllByText("320kg")[0]).toBeInTheDocument();
    expect(screen.getByText("Set 1: 8 reps x 20kg = 160kg")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Coach notes for Maya Levi"), { target: { value: " Keep stable " } });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    expect(onSave).toHaveBeenCalledWith(10, {
      coach_notes: "Keep stable",
      next_focus: "Squat depth"
    });
  });
});
