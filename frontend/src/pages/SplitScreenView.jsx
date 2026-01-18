import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  CircularProgress,
  Alert,
  Drawer,
  Typography,
  Divider,
  Stack
} from '@mui/material';
import { clientService } from '../services/clientService';
import SplitScreenSession from '../components/session/SplitScreenSession';
import TrainerControlsPanel from '../components/session/TrainerControlsPanel';

const SplitScreenView = () => {
  const { id: sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedClient, setSelectedClient] = useState(null);
  const [restTimeByClient, setRestTimeByClient] = useState({});

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await clientService.getSession(sessionId);
        setSession(res.data);
      } catch (err) {
        setError('Failed to load session');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [sessionId]);

  if (loading) return <CircularProgress sx={{ mt: 4, display: 'block', margin: '50vh auto' }} />;
  if (error) return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;

  const handleSelectClient = (client) => {
    setSelectedClient(client);
  };

  const handleRestTimeUpdate = (clientId, restTime) => {
    setRestTimeByClient((prev) => ({
      ...prev,
      [clientId]: restTime
    }));
  };

  const handleCloseDetails = () => {
    setSelectedClient(null);
  };

  useEffect(() => {
    if (!selectedClient || !session?.clients) return;
    const updatedClient = session.clients.find((client) => client.id === selectedClient.id);
    if (updatedClient && updatedClient !== selectedClient) {
      setSelectedClient(updatedClient);
    }
  }, [selectedClient, session]);

  const getRestTimeForSelected = () => {
    if (!selectedClient) return null;
    return restTimeByClient[selectedClient.id] ?? selectedClient.rest_seconds ?? null;
  };

  const currentExercise = selectedClient
    ? selectedClient.program.exercises[selectedClient.current_exercise_index]
    : null;

  return (
    <Box sx={{ height: '100vh', bgcolor: '#f5f5f5', overflow: 'hidden' }}>
      <TrainerControlsPanel
        sessionId={sessionId}
        onEndSession={() => navigate('/trainer/dashboard')}
      />

      <Container maxWidth={false} sx={{ p: 1, height: 'calc(100% - 80px)' }}>
        <SplitScreenSession
          sessionId={sessionId}
          session={session}
          onSelect={handleSelectClient}
          onRestTimeUpdate={handleRestTimeUpdate}
          onSessionUpdate={setSession}
        />
      </Container>

      <Drawer
        anchor="right"
        open={Boolean(selectedClient)}
        onClose={handleCloseDetails}
        PaperProps={{ sx: { width: { xs: '100%', sm: 360 }, p: 2 } }}
      >
        {selectedClient ? (
          <Stack spacing={2} sx={{ height: '100%' }}>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                {selectedClient.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedClient.program.name}
              </Typography>
            </Box>
            <Divider />
            {currentExercise ? (
              <Stack spacing={1}>
                <Typography variant="subtitle1" fontWeight="bold">
                  Current Exercise
                </Typography>
                <Typography variant="h6">{currentExercise.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {currentExercise.sets} sets × {currentExercise.reps} reps @ {currentExercise.weight_kg}kg
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Exercise {selectedClient.current_exercise_index + 1} of {selectedClient.program.exercises.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Set {selectedClient.current_set} of {currentExercise.sets}
                </Typography>
              </Stack>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No exercise details available.
              </Typography>
            )}
            <Divider />
            <Stack spacing={1}>
              <Typography variant="subtitle1" fontWeight="bold">
                Status
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedClient.status.replace('_', ' ').toUpperCase()}
              </Typography>
              {selectedClient.status === 'resting' && (
                <Typography variant="body1" fontWeight="bold" color="warning.main">
                  ⏱ Rest: {Math.floor((getRestTimeForSelected() || 0) / 60)}:
                  {String((getRestTimeForSelected() || 0) % 60).padStart(2, '0')}
                </Typography>
              )}
            </Stack>
          </Stack>
        ) : null}
      </Drawer>
    </Box>
  );
};

export default SplitScreenView;
