import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Typography, Button, Grid, Alert, Snackbar } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { clientService } from '../services/clientService';
import ClientCard from '../components/client/ClientCard';
import ClientFormModal from '../components/client/ClientFormModal';
import ConfirmDialog from '../components/client/ConfirmDialog';
import ExerciseLibrary from '../components/exercise/ExerciseLibrary';
import StartSessionModal from '../components/session/StartSessionModal';

const TrainerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openModal, setOpenModal] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [openConfirm, setOpenConfirm] = useState(false);
  const [clientToDelete, setClientToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [openExerciseLibrary, setOpenExerciseLibrary] = useState(false);
  const [openSessionModal, setOpenSessionModal] = useState(false);

  const fetchClients = async () => {
    try {
      const response = await clientService.getClients();
      setClients(response.data);
    } catch (err) {
      setError('Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleCreate = async (clientData) => {
    try {
      const response = await clientService.createClient(clientData);
      setClients([...clients, response.data]);
      setSnackbar({ open: true, message: 'Client created successfully!', severity: 'success' });
      setOpenModal(false);
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.error || 'Failed to create client', severity: 'error' });
    }
  };

  const handleUpdate = async (clientData) => {
    try {
      const response = await clientService.updateClient(editingClient.id, clientData);
      setClients(clients.map(c => c.id === editingClient.id ? response.data : c));
      setSnackbar({ open: true, message: 'Client updated successfully!', severity: 'success' });
      setOpenModal(false);
      setEditingClient(null);
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.error || 'Failed to update client', severity: 'error' });
    }
  };

  const handleDeactivate = async () => {
    try {
      await clientService.deactivateClient(clientToDelete.id);
      setClients(clients.filter(c => c.id !== clientToDelete.id));
      setSnackbar({ open: true, message: 'Client deactivated!', severity: 'info' });
      setOpenConfirm(false);
      setClientToDelete(null);
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to deactivate client', severity: 'error' });
    }
  };

  const handleSubmit = editingClient ? handleUpdate : handleCreate;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Welcome, {user?.full_name}!</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" onClick={() => setOpenModal(true)}>
            Add Client
          </Button>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/trainer/program/new')} 
          >
            Create Program
          </Button>
           <Button 
            variant="contained" 
            color="primary"
            onClick={() => setOpenSessionModal(true)}
          >
            Start Training Session
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Grid container spacing={3}>
        {clients.map((client) => (
          <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={client.id}>
            <ClientCard
              client={client}
              onEdit={(client) => {
                setEditingClient(client);
                setOpenModal(true);
              }}
              onDeactivate={(client) => {
                setClientToDelete(client);
                setOpenConfirm(true);
              }}
            />
          </Grid>
        ))}
        {clients.length === 0 && !loading && (
          <Grid size={{ xs: 12 }}>
            <Typography variant="body1" color="text.secondary" align="center">
              No active clients yet. Add your first client!
            </Typography>
          </Grid>
        )}
      </Grid>

      <ClientFormModal
        open={openModal}
        onClose={() => {
          setOpenModal(false);
          setEditingClient(null);
        }}
        onSubmit={handleSubmit}
        initialData={editingClient}
      />

      <ConfirmDialog
        open={openConfirm}
        onClose={() => {
          setOpenConfirm(false);
          setClientToDelete(null);
        }}
        onConfirm={handleDeactivate}
        title="Deactivate Client"
        content={`Are you sure you want to deactivate ${clientToDelete?.name}? They will be archived but data preserved.`}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />

      <ExerciseLibrary
        open={openExerciseLibrary}
        onClose={() => setOpenExerciseLibrary(false)}
        onAddExercise={(exercise) => {
          console.log('Selected exercise:', exercise);
          //  FC-4
        }}
      />
      <StartSessionModal
        open={openSessionModal}
        onClose={() => setOpenSessionModal(false)}
      />
    </Container>
  );
};

export default TrainerDashboard; 