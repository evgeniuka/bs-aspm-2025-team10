import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import { MemoryRouter } from 'react-router-dom';

import Login from '../Login';

const mockNavigate = jest.fn();
const mockSetUser = jest.fn();

jest.mock('axios');
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});
jest.mock('../../../context/AuthContext', () => ({
  useAuth: () => ({ setUser: mockSetUser }),
}));

describe('Trainer login form', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('renders email, password, and login button', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    expect(axios.post).not.toHaveBeenCalled();
  });

  it('redirects to trainer dashboard on successful login', async () => {
    const user = userEvent.setup();

    axios.post.mockResolvedValue({
      data: {
        token: 'token-value',
        user: {
          id: 1,
          email: 'trainer@example.com',
          role: 'trainer',
        },
      },
    });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText(/email/i), 'trainer@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/trainer/dashboard');
    });

    expect(mockSetUser).toHaveBeenCalledWith(
      expect.objectContaining({ role: 'trainer' })
    );
  });
});
