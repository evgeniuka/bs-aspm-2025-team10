import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Container, CircularProgress, Alert } from '@mui/material';
import { clientService } from '../services/clientService';
import { socketService } from '../services/socket';
import ClientQuadrant from '../components/session/ClientQuadrant';
import TrainerControlsPanel from '../components/session/TrainerControlsPanel';

const borderColors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']; 

const SplitScreenView = () => {
  const { id: sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const handleEndSession = async () => {
    try {
      socketService.leaveSession(sessionId);
      socketService.disconnect();
      await clientService.endSession(sessionId);
      setTimeout(() => {
        navigate('/trainer/dashboard');
      }, 100);
    } catch (err) {
      console.error('Failed to end session:', err);
      navigate('/trainer/dashboard'); 
    }
  };

  <TrainerControlsPanel
    sessionId={sessionId}
    onEndSession={handleEndSession}
  />

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


  useEffect(() => {
    if (!sessionId) return;

    const socket = socketService.connect();
    socketService.joinSession(sessionId);

    socketService.onSessionUpdate((data) => {
      console.log('🔄 Session update received:', data);
      
      // Trigger pulse animation
      const quadrantElement = document.getElementById(`client-${data.client_id}`);
      if (quadrantElement) {
        quadrantElement.classList.add('pulse-animation');
        setTimeout(() => {
          quadrantElement.classList.remove('pulse-animation');
        }, 300);
      }
      
      setSession(prevSession => {
        if (!prevSession) return prevSession;
        return {
          ...prevSession,
          clients: prevSession.clients.map(client =>
            client.id === data.client_id
              ? { ...client, ...data.updated_client_data }
              : client
          )
        };
      });
    });

    return () => {
      socketService.offSessionUpdate();
      socketService.leaveSession(sessionId);
      socketService.disconnect();
    };
  }, [sessionId]);


  if (loading) {
    return (
      <CircularProgress
        sx={{ mt: 4, display: 'block', margin: '50vh auto' }}
      />
    );
  }

  if (error) {
    return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;
  }

  const clients = session?.clients?.slice(0, 4) || [];
  const totalSlots = 4;

  return (
    <Box sx={{ height: '100vh', bgcolor: '#f5f5f5', overflow: 'hidden' }}>
      <TrainerControlsPanel
        sessionId={sessionId}
        onEndSession={() => navigate('/trainer/dashboard')}
      />

      {/* 2×2 Grid */}
      <Container maxWidth={false} sx={{ p: 1, height: 'calc(100% - 80px)' }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            gridTemplateRows: { xs: 'auto auto', sm: '1fr 1fr' },
            gap: 1,
            height: '100%',
          }}
        >
          {Array.from({ length: totalSlots }).map((_, idx) => {
            const client = clients[idx];
            return client ? (
              <ClientQuadrant
                key={client.id}
                client={client}
                borderColor={borderColors[idx]}
                sessionId={sessionId} 
              />
            ) : (
              <Box
                key={`empty-${idx}`}
                sx={{
                  border: '2px dashed #ccc',
                  borderRadius: 2,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  fontSize: '1.2rem',
                  color: '#999',
                  bgcolor: '#fff'
                }}
              >
                Empty Slot
              </Box>
            );
          })}
        </Box>
      </Container>
    </Box>
  );
};

export default SplitScreenView;