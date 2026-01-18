import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import TrainerDashboard from '../TrainerDashboard';
import { clientService } from '../../services/clientService';

vi.mock('../../services/clientService', () => ({
  clientService: {
    getClients: vi.fn(),
    createClient: vi.fn(),
    updateClient: vi.fn(),
    deactivateClient: vi.fn(),
    getMyClient: vi.fn(),
  },
}));

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { full_name: 'Test Trainer' } }),
}));

describe('TrainerDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('test_client_dashboard_renders', async () => {
    clientService.getClients.mockResolvedValue({
      data: [
        {
          id: 1,
          name: 'Taylor Client',
          age: 29,
          fitness_level: 'Beginner',
          goals: 'Improve overall strength and conditioning',
          active: true,
          last_workout_date: null,
        },
      ],
    });

    render(<TrainerDashboard />);

    expect(await screen.findByText('Taylor Client')).toBeInTheDocument();
    expect(screen.getByText(/Age: 29/)).toBeInTheDocument();
  });

  it('test_add_client_modal', async () => {
    clientService.getClients.mockResolvedValue({ data: [] });
    clientService.createClient.mockResolvedValue({
      data: {
        id: 2,
        name: 'Jordan Client',
        age: 33,
        fitness_level: 'Intermediate',
        goals: 'Build endurance for upcoming races',
        active: true,
      },
    });

    render(<TrainerDashboard />);

    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: /add client/i }));

    await user.type(screen.getByLabelText(/name/i), 'Jordan Client');
    await user.type(screen.getByLabelText(/age/i), '33');
    await user.type(screen.getByLabelText(/goals/i), 'Build endurance for upcoming races');

    await user.click(screen.getByRole('button', { name: /create client/i }));

    await waitFor(() => {
      expect(clientService.createClient).toHaveBeenCalledWith({
        name: 'Jordan Client',
        age: 33,
        fitness_level: 'Beginner',
        goals: 'Build endurance for upcoming races',
      });
    });
  });
});
