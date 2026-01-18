import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ClientQuadrant from '../ClientQuadrant';
import { clientService } from '../../../services/clientService';

vi.mock('../../../services/clientService', () => ({
  clientService: {
    markSetComplete: vi.fn()
  }
}));

const baseClient = {
  id: 1,
  name: 'Test Client',
  status: 'active',
  current_exercise_index: 0,
  current_set: 1,
  rest_time_remaining: 0,
  program: {
    name: 'Strength Plan',
    exercises: [
      {
        id: 10,
        name: 'Squat',
        sets: 4,
        reps: 8,
        weight_kg: 60,
        rest_seconds: 30
      }
    ]
  }
};

const renderQuadrant = (clientOverrides = {}) => {
  render(
    <ClientQuadrant
      client={{ ...baseClient, ...clientOverrides }}
      borderColor="#2196F3"
      sessionId="1"
    />
  );
};

describe('ClientQuadrant', () => {
  beforeEach(() => {
    clientService.markSetComplete.mockResolvedValue({});
  });

  it('enables mark complete button when active', async () => {
    renderQuadrant({ status: 'active' });

    fireEvent.click(screen.getByText('Test Client'));
    const button = await screen.findByRole('button', { name: /mark set complete/i });

    expect(button).toBeEnabled();
  });

  it('disables mark complete button when resting', async () => {
    renderQuadrant({ status: 'resting', rest_time_remaining: 20 });

    fireEvent.click(screen.getByText('Test Client'));
    const button = await screen.findByRole('button', { name: /mark set complete/i });

    expect(button).toBeDisabled();
  });

  it('optimistically increments the set when clicking mark complete', async () => {
    const user = userEvent.setup();
    clientService.markSetComplete.mockImplementation(
      () => new Promise(() => {})
    );

    renderQuadrant({ status: 'active' });
    fireEvent.click(screen.getByText('Test Client'));

    const button = await screen.findByRole('button', { name: /mark set complete/i });
    await user.click(button);

    expect(screen.getByText(/Set 2 of 4/i)).toBeInTheDocument();
  });
});
