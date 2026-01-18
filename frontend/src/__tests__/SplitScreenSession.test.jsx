import React from 'react';
import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { vi } from 'vitest';
import SplitScreenSession from '../components/session/SplitScreenSession';

let sessionUpdateHandler;

vi.mock('../services/socket', () => ({
  socketService: {
    connect: vi.fn(),
    joinSession: vi.fn(),
    leaveSession: vi.fn(),
    onSessionUpdate: vi.fn((handler) => {
      sessionUpdateHandler = handler;
    }),
    offSessionUpdate: vi.fn(),
    disconnect: vi.fn()
  }
}));

const buildClient = (id, overrides = {}) => ({
  id,
  name: `Client ${id}`,
  status: 'ready',
  current_exercise_index: 0,
  current_set: 1,
  program: {
    name: 'Program A',
    exercises: [
      {
        name: 'Squat',
        sets: 3,
        reps: 10,
        weight_kg: 100,
        rest_seconds: 60
      }
    ]
  },
  ...overrides
});

describe('SplitScreenSession', () => {
  it('test_split_screen_renders_4_quadrants', () => {
    const session = {
      id: 1,
      clients: [1, 2, 3, 4].map((id) => buildClient(id))
    };

    render(<SplitScreenSession sessionId="1" session={session} />);

    expect(screen.getAllByTestId('client-quadrant')).toHaveLength(4);
  });

  it('test_empty_quadrants_shown', () => {
    const session = {
      id: 1,
      clients: [1, 2].map((id) => buildClient(id))
    };

    render(<SplitScreenSession sessionId="1" session={session} />);

    expect(screen.getAllByText('No client assigned')).toHaveLength(2);
  });

  it('test_websocket_updates_quadrant', () => {
    const session = {
      id: 1,
      clients: [buildClient(1, { status: 'ready' })]
    };

    render(<SplitScreenSession sessionId="1" session={session} />);

    expect(typeof sessionUpdateHandler).toBe('function');

    act(() => {
      sessionUpdateHandler({
        client_id: 1,
        updated_data: { status: 'complete' }
      });
    });

    expect(screen.getByText('✅ COMPLETE')).toBeInTheDocument();
  });
});
