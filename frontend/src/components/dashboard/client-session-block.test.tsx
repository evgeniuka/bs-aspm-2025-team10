import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ClientSessionBlock } from "./client-session-block";
import type { SessionAssignment } from "./session-setup-model";

const assignment: SessionAssignment = {
  client: {
    id: 10,
    name: "Maya Levi",
    age: 29,
    fitness_level: "Intermediate",
    goals: "Build strength while training around a busy work schedule.",
    active: true,
    last_workout_date: "2026-05-12T10:00:00Z",
    created_at: "2026-05-01T10:00:00Z"
  },
  program: {
    id: 20,
    client_id: 10,
    name: "Maya Strength Block",
    focus: "Strength Block",
    notes: null,
    is_session_snapshot: false,
    created_at: "2026-05-01T10:00:00Z",
    exercises: [
      {
        id: 1,
        order_index: 0,
        sets: 3,
        reps: 8,
        weight_kg: 20,
        rest_seconds: 60,
        notes: null,
        exercise: {
          id: 1,
          name: "Goblet Squat",
          category: "Strength",
          equipment: "Kettlebell",
          difficulty: "Beginner",
          description: "Squat pattern"
        }
      },
      {
        id: 2,
        order_index: 1,
        sets: 3,
        reps: 10,
        weight_kg: 15,
        rest_seconds: 60,
        notes: null,
        exercise: {
          id: 2,
          name: "TRX Row",
          category: "Strength",
          equipment: "TRX",
          difficulty: "Beginner",
          description: "Pulling pattern"
        }
      }
    ]
  }
};

afterEach(() => cleanup());

describe("ClientSessionBlock", () => {
  it("renders an empty state before a client is selected", () => {
    render(<ClientSessionBlock assignments={[]} />);

    expect(screen.getByText("Client block")).toBeInTheDocument();
    expect(screen.getByText("No client selected")).toBeInTheDocument();
  });

  it("renders client goals and selected plan context", () => {
    render(<ClientSessionBlock assignments={[assignment]} />);

    expect(screen.getByText("Maya Levi")).toBeInTheDocument();
    expect(screen.getByText("Build strength while training around a busy work schedule.")).toBeInTheDocument();
    expect(screen.getByText("6 sets / 930kg")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Profile/i })).toHaveAttribute("href", "/clients/10");
    expect(screen.getByRole("link", { name: /Plan/i })).toHaveAttribute("href", "/programs/20");
  });
});
