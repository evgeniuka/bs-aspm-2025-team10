import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Paper,
  Button,
  Snackbar,
  Alert,
  CircularProgress  
} from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import { clientService } from '../../services/clientService';

const ClientQuadrant = ({ client, borderColor, sessionId }) => {
  const [optimisticClient, setOptimisticClient] = useState(client);
  const currentExerciseIndex = optimisticClient.current_exercise_index;
  const currentExercise = optimisticClient.program.exercises[currentExerciseIndex];
  const totalExercises = optimisticClient.program.exercises.length;
  const [restTime, setRestTime] = useState(
    optimisticClient.rest_time_remaining || currentExercise?.rest_seconds || 60
  );

  const [showCompleteButton, setShowCompleteButton] = useState(false);
  const [loading, setLoading] = useState(false); 
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    setOptimisticClient(client);
  }, [client]);

  useEffect(() => {
    const exercise = optimisticClient.program.exercises[optimisticClient.current_exercise_index];
    setRestTime(optimisticClient.rest_time_remaining || exercise?.rest_seconds || 60);
  }, [
    optimisticClient.current_exercise_index, 
    optimisticClient.program.exercises, 
    optimisticClient.rest_time_remaining
  ]);

  useEffect(() => {
    let interval;
    if (optimisticClient.status === 'resting' && restTime > 0) {
      interval = setInterval(() => {
        setRestTime(prev => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [optimisticClient.status, restTime]);

  const overallProgress = totalExercises > 0
    ? ((currentExerciseIndex + 1) / totalExercises) * 100
    : 0;

  const handleTap = () => {
    if (optimisticClient.status === 'complete' || optimisticClient.status === 'completed') return;
    setShowCompleteButton(prev => !prev); 
  };

  const handleMarkComplete = async () => {
    setLoading(true);  
    setOptimisticClient(prev => {
      const exercise = prev.program.exercises[prev.current_exercise_index];
      if (!exercise) return prev;
      const totalSets = exercise.sets || 0;
      if (prev.current_set < totalSets) {
        return {
          ...prev,
          current_set: prev.current_set + 1,
          status: 'resting',
          rest_time_remaining: exercise.rest_seconds || prev.rest_time_remaining
        };
      }

      const nextExerciseIndex = prev.current_exercise_index + 1;
      const nextStatus = nextExerciseIndex >= prev.program.exercises.length ? 'completed' : 'active';

      return {
        ...prev,
        current_exercise_index: nextExerciseIndex,
        current_set: 1,
        status: nextStatus,
        rest_time_remaining: 0
      };
    });
    
    try {
      await clientService.markSetComplete(sessionId, {
        client_id: optimisticClient.id,
        exercise_id: currentExercise.id,
        set_number: optimisticClient.current_set
      });

      setShowCompleteButton(false); 

      setSnackbar({
        open: true,
        message: 'Set marked as complete!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Failed to mark complete:', err);
      setSnackbar({
        open: true,
        message: 'Failed to mark complete. Tap again.',
        severity: 'error'
      });

    } finally {
      setLoading(false); 
    }
  };

  return (
    <Paper
      id={`client-${client.id}`} 
      onClick={handleTap}
      elevation={3}
      sx={{
        position: 'relative',  
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
        bgcolor: optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? '#e8f5e9' : '#fff',
        borderLeft: `8px solid ${borderColor}`,
        transition: 'all 0.3s ease',
        cursor: optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? 'default' : 'pointer',
        opacity: optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? 0.7 : 1,
        pointerEvents: optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? 'none' : 'auto',
        '&:hover': {
          borderLeftWidth: optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? '8px' : '12px',
          boxShadow: optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? 3 : 6
        }
      }}
    >
      {/* Wrapper for absolute positioning */}
      <Box position="relative" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        
        {/* Semi-transparent backdrop */}
        {showCompleteButton && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              bgcolor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 9,
              borderRadius: 1
            }}
          />
        )}

        {/*  Complete Button Overlay */}
        {showCompleteButton && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '60%',
              zIndex: 10
            }}
          >
            <Button
              variant="contained"
              color="success"
              startIcon={loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : <CheckIcon />}
              onClick={(e) => {
                e.stopPropagation();
                handleMarkComplete();
              }}
              disabled={loading || optimisticClient.status === 'resting'}  
              sx={{
                width: '100%',
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Saving...' : 'Mark Set Complete'}
            </Button>
          </Box>
        )}

        {/* Client Info */}
        <Box>
          <Typography variant="h5" fontWeight="bold" sx={{ color: borderColor }}>
            {optimisticClient.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {optimisticClient.program.name}
          </Typography>
        </Box>

        {/* Exercise Info */}
        {currentExercise ? (
          <>
            <Box sx={{ my: 2 }}>
              <Typography
                variant="h4"
                fontWeight="bold"
                sx={{ fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' } }}
              >
                {currentExercise.name.toUpperCase()}
              </Typography>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
              >
                {currentExercise.sets} sets × {currentExercise.reps} reps @ {currentExercise.weight_kg}kg
              </Typography>
            </Box>

            <LinearProgress
              variant="determinate"
              value={overallProgress}
              sx={{ 
                mb: 1, 
                height: 8, 
                borderRadius: 1,
                transition: 'all 0.3s ease'  
              }}
            />
            <Typography variant="body2" fontWeight="bold">
              Exercise {currentExerciseIndex + 1} of {totalExercises}
            </Typography>

            <Typography variant="body1" sx={{ mt: 1 }}>
              Set {optimisticClient.current_set} of {currentExercise.sets}
            </Typography>
          </>
        ) : (
          <Typography>No exercises</Typography>
        )}

        {/* Status Display */}
        <Box sx={{ mt: 2, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
          {optimisticClient.status === 'resting' && restTime > 0 ? (
            <Typography variant="h5" fontWeight="bold" color="warning.main" align="center">
              ⏱ REST: {Math.floor(restTime / 60)}:{String(restTime % 60).padStart(2, '0')}
            </Typography>
          ): optimisticClient.status === 'resting' && restTime === 0 ? (
            <Button 
              variant="contained" 
              color="success"
              onClick={handleMarkComplete}
              sx={{ width: '100%' }}
            >
              Start Next Set
            </Button>
          ) : optimisticClient.status === 'complete' || optimisticClient.status === 'completed' ? (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                ✅ WORKOUT COMPLETE!
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                {totalExercises}/{totalExercises} exercises completed
              </Typography>
            </Box>
          ) : (
            <Typography
              variant="h6"
              fontWeight="bold"
              align="center"
              sx={{
                color:
                  optimisticClient.status === 'ready' || optimisticClient.status === 'active'
                    ? 'success.main'
                    : optimisticClient.status === 'in_progress'
                    ? 'warning.main'
                    : 'inherit'
              }}
            >
              {(optimisticClient.status === 'ready' || optimisticClient.status === 'active') && '✓ READY'}
              {optimisticClient.status === 'in_progress' && '🔥 IN PROGRESS'}
            </Typography>
          )}
        </Box>

      </Box>  {/* Close relative wrapper */}

      {/* Snackbar notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default ClientQuadrant;
