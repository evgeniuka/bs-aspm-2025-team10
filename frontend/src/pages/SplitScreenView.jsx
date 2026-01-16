import React, { useState, useEffect, useRef } from 'react';
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
  const socketInitialized = useRef(false);  
  const handleEndSession = (summaryData) => {
    try {
      console.log('🛑 Ending session, navigating away');
      
      if (summaryData) {
        navigate(`/session-summary/${sessionId}`, { state: { summary: summaryData } });
      } else {
        navigate('/trainer/dashboard');
      }
    } catch (err) {
      console.error('❌ Navigation failed:', err);
      navigate('/trainer/dashboard');
    }
  };


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
    if (!sessionId || loading || socketInitialized.current) return;

    console.log('🔌 Initializing WebSocket for session', sessionId);
    socketInitialized.current = true;  

    const socket = socketService.connect();
    socketService.joinSession(sessionId);

    
    socketService.onSessionUpdate((data) => {
      console.log('🔄 Session update received:', data);

     
      const quadrantElement = document.getElementById(`client-${data.client_id}`);
      if (quadrantElement) {
        quadrantElement.classList.add('pulse-animation');
        setTimeout(() => {
          quadrantElement.classList.remove('pulse-animation');
        }, 300);
      }

      setSession((prevSession) => {
        if (!prevSession) return prevSession;
        return {
          ...prevSession,
          clients: prevSession.clients.map((client) =>
            client.id === data.client_id
              ? { ...client, ...data.updated_client_data }
              : client
          ),
        };
      });
    });


    socketService.onSessionEnded((data) => {
      console.log('🛑 Session ended by trainer:', data);
       setTimeout(() => {
      socketService.disconnect();
      navigate('/trainer/dashboard');
    }, 500);
    });

  
    return () => {
      console.log('🧹 Cleanup: Closing socket via useEffect');
      socketService.offSessionUpdate();
      socketService.offSessionEnded();
      socketService.leaveSession(sessionId);
      socketService.disconnect();
      socketInitialized.current = false;  
    };
  }, [sessionId, loading, navigate]);

  if (loading) {
    return <CircularProgress sx={{ mt: 4, display: 'block', margin: '50vh auto' }} />;
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
        onEndSession={handleEndSession}
        session={session}
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
                  bgcolor: '#fff',
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
