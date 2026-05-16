import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CockpitQuadrant } from "./cockpit-quadrant";
import type { SessionParticipant } from "@/lib/types";

const participant: SessionParticipant = {
  id: 1,
  client_id: 10,
  client_name: "Maya Levi",
  current_exercise_index: 0,
  current_set: 1,
  status: "ready",
  completed_exercises: [],
  rest_time_remaining: 0,
  coach_notes: null,
  next_focus: null,
  today_check_in: null,
  sets_completed: [],
  program: {
    id: 1,
    client_id: 10,
    name: "Strength Block",
    focus: "Strength Block",
    notes: null,
    is_session_snapshot: false,
    created_at: new Date().toISOString(),
    exercises: [
      {
        id: 1,
        order_index: 0,
        sets: 3,
        reps: 10,
        weight_kg: 25,
        rest_seconds: 45,
        notes: null,
        exercise: {
          id: 1,
          name: "Goblet Squat",
          category: "Strength",
          equipment: "Kettlebell",
          difficulty: "Beginner",
          description: "Squat pattern"
        }
      }
    ]
  }
};

afterEach(() => cleanup());

describe("CockpitQuadrant", () => {
  it("renders current trainee and exercise", () => {
    render(<CockpitQuadrant participant={participant} onCompleteSet={vi.fn()} onStartNextSet={vi.fn()} onUndoLastSet={vi.fn()} />);

    expect(screen.getByText("Maya Levi")).toBeInTheDocument();
    expect(screen.getByText("Goblet Squat")).toBeInTheDocument();
    expect(screen.getByText("0/3")).toBeInTheDocument();
    expect(screen.getByLabelText("Actual reps for Maya Levi")).toHaveValue(10);
    expect(screen.getByLabelText("Actual weight for Maya Levi")).toHaveValue(25);
    expect(screen.getByRole("button", { name: /complete set/i })).toBeEnabled();
  });

  it("submits actual reps and weight and shows undo after a completed set", () => {
    const onCompleteSet = vi.fn();
    const onUndoLastSet = vi.fn();
    render(
      <CockpitQuadrant
        participant={{
          ...participant,
          sets_completed: [
            {
              program_exercise_id: 1,
              exercise_id: 1,
              exercise_name: "Goblet Squat",
              set_number: 1,
              reps_completed: 9,
              weight_kg: 27.5,
              volume_kg: 247.5,
              created_at: new Date().toISOString()
            }
          ]
        }}
        onCompleteSet={onCompleteSet}
        onStartNextSet={vi.fn()}
        onUndoLastSet={onUndoLastSet}
      />
    );

    fireEvent.change(screen.getByLabelText("Actual reps for Maya Levi"), { target: { value: "9" } });
    fireEvent.change(screen.getByLabelText("Actual weight for Maya Levi"), { target: { value: "27.5" } });
    fireEvent.click(screen.getByRole("button", { name: /complete set/i }));

    expect(onCompleteSet).toHaveBeenCalledWith(10, {
      program_exercise_id: 1,
      exercise_id: 1,
      set_number: 1,
      reps_completed: 9,
      weight_kg: 27.5
    });

    fireEvent.click(screen.getByRole("button", { name: /undo last set/i }));
    expect(onUndoLastSet).toHaveBeenCalledWith(10);
  });
});
