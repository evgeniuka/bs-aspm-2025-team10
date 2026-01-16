import React, { useState, useEffect } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { clientService } from '../../services/clientService';
import EndSessionDialog from './EndSessionDialog';

const TrainerControlsPanel = ({ sessionId, onEndSession, session }) => {
  const [duration, setDuration] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false); 
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    const timer = setInterval(() => setDuration(prev => prev + 1), 1000);
    return () => clearInterval(timer);
  }, []);



  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleEndSession = async () => {
    setLoading(true);
    try {
      const response = await clientService.endSession(sessionId);

      onEndSession(response.data.summary);
    } catch (err) {
      console.error('Failed to end session:', err);
      

      if (err.response?.status === 400 || err.response?.status === 404) {
        onEndSession(null); 
      } else {
        alert('Network error. Please check your connection.');
      }
    } finally {
      setLoading(false);
      setDialogOpen(false);
    }
  };

  return (
    <Box
      sx={{
        p: 1,
        bgcolor: '#333',
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}
    >
      <Typography variant="h6">Session #{sessionId}</Typography>
      <Typography variant="body1">Duration: {formatTime(duration)}</Typography>

      <Button
        variant="contained"
        color="error"
        onClick={() => setDialogOpen(true)}
        startIcon={<span>⏹</span>}
        sx={{ 
          minWidth: 48, 
          minHeight: 48,
          px: 2
        }}
      >
        End Session
      </Button>
      
      <EndSessionDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onConfirm={handleEndSession}
        session={session} 
        loading={loading}
      />

    </Box>
  );
};

export default TrainerControlsPanel;