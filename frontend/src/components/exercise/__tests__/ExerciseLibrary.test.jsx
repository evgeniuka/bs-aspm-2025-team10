import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ExerciseLibrary from '../ExerciseLibrary';

const mockGetExercises = vi.fn();

vi.mock('../../../services/clientService', () => ({
  clientService: {
    getExercises: () => mockGetExercises(),
  },
}));

const exercises = [
  {
    id: 1,
    name: 'Bench Press',
    category: 'upper_body',
    equipment: 'barbell',
    difficulty: 'intermediate',
    description: 'Chest exercise',
  },
  {
    id: 2,
    name: 'Back Squat',
    category: 'lower_body',
    equipment: 'barbell',
    difficulty: 'intermediate',
    description: 'Leg exercise',
  },
];

describe('ExerciseLibrary', () => {
  beforeEach(() => {
    mockGetExercises.mockResolvedValue({ data: exercises });
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
    mockGetExercises.mockReset();
  });

  it('renders exercise cards from the API', async () => {
    render(<ExerciseLibrary open onClose={() => {}} onAddExercise={() => {}} />);

    expect(await screen.findByText('Bench Press')).toBeInTheDocument();
    expect(screen.getByText('Back Squat')).toBeInTheDocument();
  });

  it('filters exercises by search input', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<ExerciseLibrary open onClose={() => {}} onAddExercise={() => {}} />);

    await screen.findByText('Bench Press');

    const searchInput = screen.getByPlaceholderText('Search exercises...');
    await user.clear(searchInput);
    await user.type(searchInput, 'bench press');

    act(() => {
      vi.advanceTimersByTime(350);
    });

    expect(screen.getByText('Bench Press')).toBeInTheDocument();
    expect(screen.queryByText('Back Squat')).not.toBeInTheDocument();
  });
});
