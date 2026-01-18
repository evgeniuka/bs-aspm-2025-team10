import React from 'react';
import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { vi } from 'vitest';
import RestTimer from '../components/session/RestTimer';

describe('RestTimer', () => {
  it('test_rest_timer_counts_down', () => {
    vi.useFakeTimers();
    render(<RestTimer initialSeconds={120} running />);

    expect(screen.getByText('⏱ REST: 2:00')).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(screen.getByText('⏱ REST: 1:59')).toBeInTheDocument();
    vi.useRealTimers();
  });
});
