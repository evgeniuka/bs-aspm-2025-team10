import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProgramBuilder from '../ProgramBuilder';

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1, role: 'trainer' } }),
}));

const mockCreateProgram = vi.fn();
const mockGetClients = vi.fn();
const mockGetExercises = vi.fn();

vi.mock('../../services/clientService', () => ({
  clientService: {
    getClients: (...args) => mockGetClients(...args),
    getExercises: (...args) => mockGetExercises(...args),
    createProgram: (...args) => mockCreateProgram(...args),
  },
}));

const buildExercise = (id) => ({
  id,
  name: `Exercise ${id}`,
  category: 'upper_body',
  description: 'Test description',
  equipment: 'bodyweight',
  difficulty: 'beginner',
});

describe('ProgramBuilder', () => {
  beforeEach(() => {
    mockGetClients.mockResolvedValue({
      data: [{ id: 10, name: 'Client One' }],
    });
    mockGetExercises.mockResolvedValue({
      data: [buildExercise(1), buildExercise(2), buildExercise(3), buildExercise(4), buildExercise(5)],
    });
    mockCreateProgram.mockResolvedValue({ data: { id: 99 } });
  });

  afterEach(() => {
    mockGetClients.mockReset();
    mockGetExercises.mockReset();
    mockCreateProgram.mockReset();
  });

  it('renders the program builder panels', async () => {
    render(<ProgramBuilder />);

    expect(await screen.findByText('Create Workout Program')).toBeInTheDocument();
    expect(screen.getByLabelText('Program Name *')).toBeInTheDocument();
    expect(screen.getByText(/Exercises \(/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add Exercise' })).toBeInTheDocument();
  });

  it('adds an exercise to the program', async () => {
    const user = userEvent.setup();
    render(<ProgramBuilder />);

    await user.click(await screen.findByRole('button', { name: 'Add Exercise' }));
    await screen.findByText('Exercise Library');

    const [firstAdd] = await screen.findAllByRole('button', { name: 'Add' });
    await user.click(firstAdd);
    await user.click(await screen.findByRole('button', { name: 'Confirm' }));

    expect(await screen.findByText('Exercise 1')).toBeInTheDocument();
  });

  it('saves a program', async () => {
    const user = userEvent.setup();
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    const backSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {});

    render(<ProgramBuilder />);

    await user.type(await screen.findByLabelText('Program Name *'), 'My Program');
    await user.click(screen.getByRole('button', { name: 'Select Client *' }));
    await user.click(await screen.findByRole('option', { name: 'Client One' }));

    await user.click(await screen.findByRole('button', { name: 'Add Exercise' }));
    await screen.findByText('Exercise Library');

    const addButtons = await screen.findAllByRole('button', { name: 'Add' });
    for (const button of addButtons) {
      await user.click(button);
    }
    await user.click(await screen.findByRole('button', { name: 'Confirm' }));

    const saveButton = screen.getByRole('button', { name: 'Save Program' });
    await waitFor(() => expect(saveButton).toBeEnabled());
    await user.click(saveButton);

    await waitFor(() => expect(mockCreateProgram).toHaveBeenCalledTimes(1));

    alertSpy.mockRestore();
    backSpy.mockRestore();
  });
});
