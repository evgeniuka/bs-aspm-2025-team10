import React, { useState, useEffect } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { clientService } from '../../services/clientService';

const TrainerControlsPanel = ({ sessionId, onEndSession }) => {
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setDuration(prev => prev + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleEnd = async () => {
    try {
      await clientService.endSession(sessionId); 
    } catch (err) {
      console.error('Failed to end session:', err);
    } finally {
      onEndSession(); 
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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
        onClick={handleEnd}
        sx={{ color: 'white' }}
      >
        End Session
      </Button>
    </Box>
  );
};

export default TrainerControlsPanel;