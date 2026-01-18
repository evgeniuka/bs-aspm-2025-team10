import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SplitScreenView from '../SplitScreenView';
import { clientService } from '../../services/clientService';
import { socketService } from '../../services/socket';

let sessionUpdateHandler;

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useParams: () => ({ id: '1' })
  };
});

vi.mock('../../services/clientService', () => ({
  clientService: {
    getSession: vi.fn()
  }
}));

vi.mock('../../services/socket', () => ({
  socketService: {
    connect: vi.fn(() => ({ id: 'socket' })),
    joinSession: vi.fn(),
    onSessionUpdate: vi.fn((handler) => {
      sessionUpdateHandler = handler;
    }),
    onSessionEnded: vi.fn(),
    offSessionUpdate: vi.fn(),
    offSessionEnded: vi.fn(),
    leaveSession: vi.fn(),
    disconnect: vi.fn()
  }
}));

describe('SplitScreenView', () => {
  beforeEach(() => {
    sessionUpdateHandler = undefined;
  });

  it('syncs quadrant state on websocket session_update', async () => {
    clientService.getSession.mockResolvedValue({
      data: {
        id: 1,
        trainer_id: 2,
        status: 'active',
        created_at: new Date().toISOString(),
        clients: [
          {
            id: 1,
            name: 'Client A',
            program: {
              name: 'Plan A',
              exercises: [
                {
                  id: 10,
                  name: 'Squat',
                  sets: 3,
                  reps: 8,
                  weight_kg: 60,
                  rest_seconds: 30
                }
              ]
            },
            current_exercise_index: 0,
            current_set: 1,
            status: 'active',
            completed_exercises: [],
            rest_time_remaining: 0
          }
        ]
      }
    });

    render(<SplitScreenView />);

    expect(await screen.findByText('Client A')).toBeInTheDocument();
    expect(screen.getByText(/Set 1 of 3/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(socketService.onSessionUpdate).toHaveBeenCalled();
    });

    sessionUpdateHandler?.({
      client_id: 1,
      updated_client_data: {
        current_set: 2,
        current_exercise_index: 0,
        status: 'active',
        rest_time_remaining: 0
      }
    });

    expect(await screen.findByText(/Set 2 of 3/i)).toBeInTheDocument();
  });
});
