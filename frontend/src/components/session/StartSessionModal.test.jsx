import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';
import StartSessionModal from './StartSessionModal';
import { clientService } from '../../services/clientService';

vi.mock('../../services/clientService', () => ({
  clientService: {
    getClients: vi.fn(),
    getProgramsByClient: vi.fn(),
    createSession: vi.fn(),
  },
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

const renderModal = () =>
  render(
    <MemoryRouter>
      <StartSessionModal open onClose={() => {}} />
    </MemoryRouter>
  );

describe('StartSessionModal', () => {
  beforeEach(() => {
    clientService.getClients.mockResolvedValue({
      data: [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
      ],
    });
    clientService.getProgramsByClient.mockResolvedValue({
      data: [{ id: 10, name: 'Strength Plan', exercises: [{}, {}] }],
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders client checkboxes', async () => {
    renderModal();

    expect(await screen.findByLabelText('Alice')).toBeInTheDocument();
    expect(screen.getByLabelText('Bob')).toBeInTheDocument();
  });

  it('populates program dropdown after selecting a client', async () => {
    renderModal();

    const clientCheckbox = await screen.findByLabelText('Alice');
    fireEvent.click(clientCheckbox);

    await waitFor(() => {
      expect(clientService.getProgramsByClient).toHaveBeenCalledWith(1);
    });

    const programSelect = await screen.findByRole('combobox');
    fireEvent.mouseDown(programSelect);

    expect(await screen.findByText('Strength Plan (2 exercises)')).toBeInTheDocument();
  });

  it('enables start button once client and program are selected', async () => {
    renderModal();

    const startButton = screen.getByRole('button', { name: /start training/i });
    expect(startButton).toBeDisabled();

    const clientCheckbox = await screen.findByLabelText('Alice');
    fireEvent.click(clientCheckbox);

    const programSelect = await screen.findByRole('combobox');
    fireEvent.mouseDown(programSelect);
    fireEvent.click(await screen.findByText('Strength Plan (2 exercises)'));

    await waitFor(() => {
      expect(startButton).toBeEnabled();
    });
  });
});
