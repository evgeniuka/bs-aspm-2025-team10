import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { clientService } from '../services/clientService';
import { Box, Container, Typography, CircularProgress, Alert } from '@mui/material';

const SessionView = () => {
  const { id } = useParams();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await clientService.getSession(id);
        setSession(res.data);
      } catch (err) {
        setError('Failed to load session');
        console.error('Session load error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [id]);

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Preparing session...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Training Session — ID: {session.id}
      </Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 3 }}>
        {session.clients.map(client => (
          <Box key={client.id} sx={{ p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
            <Typography variant="h6">{client.client_name}</Typography>
            <Typography variant="body2">Program: {client.program_name}</Typography>
            <Typography variant="body2">Status: {client.status}</Typography>
            {/* split-screen logic (exercises, timers, etc.) */}
          </Box>
        ))}
      </Box>
    </Container>
  );
};

export default SessionView;