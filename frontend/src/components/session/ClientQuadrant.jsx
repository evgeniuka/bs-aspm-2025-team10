import React, { useState, useEffect } from 'react';
import { Box, Typography, LinearProgress, Paper } from '@mui/material';

const statusTexts = {
  ready: 'READY',
  in_progress: 'IN PROGRESS',
  resting: 'RESTING',
  complete: 'COMPLETE'
};

const ClientQuadrant = ({ client, borderColor, onSelect, onRestTimeUpdate }) => {
  const currentExerciseIndex = client.current_exercise_index;
  const currentExercise = client.program.exercises[currentExerciseIndex];
  const totalExercises = client.program.exercises.length;

  const [restTime, setRestTime] = useState(currentExercise?.rest_seconds || 60);

  useEffect(() => {
    const exercise = client.program.exercises[client.current_exercise_index];
    setRestTime(exercise?.rest_seconds || 60);
  }, [client.current_exercise_index, client.program.exercises]);

  useEffect(() => {
    if (onRestTimeUpdate) {
      onRestTimeUpdate(client.id, restTime);
    }
  }, [client.id, onRestTimeUpdate, restTime]);

  useEffect(() => {
    let interval;
    if (client.status === 'resting' && restTime > 0) {
      interval = setInterval(() => {
        setRestTime(prev => {
          if (prev <= 1) {
            // ✅ Когда таймер закончится, можно отправить событие "ready"
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [client.status, restTime]);

  const overallProgress = totalExercises > 0 
    ? ((currentExerciseIndex + 1) / totalExercises) * 100 
    : 0;

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
        bgcolor: client.status === 'complete' ? '#e8f5e9' : '#fff',
        borderLeft: `8px solid ${borderColor}`, // ✅ Цветная граница
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        '&:hover': {
          borderLeftWidth: '12px',
          boxShadow: 6
        }
      }}
      onClick={() => onSelect?.(client)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          onSelect?.(client);
        }
      }}
    >
      <Box>
        <Typography variant="h5" fontWeight="bold" sx={{ color: borderColor }}>
          {client.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {client.program.name}
        </Typography>
      </Box>

      {currentExercise ? (
        <>
          <Box sx={{ my: 2 }}>
            <Typography variant="h4" fontWeight="bold" sx={{ 
              fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' } 
            }}>
              {currentExercise.name.toUpperCase()}
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{
              fontSize: { xs: '1rem', sm: '1.25rem' }
            }}>
              {currentExercise.sets} sets × {currentExercise.reps} reps @ {currentExercise.weight_kg}kg
            </Typography>
          </Box>

          <LinearProgress
            variant="determinate"
            value={overallProgress}
            sx={{ mb: 1, height: 8, borderRadius: 1 }}
          />
          <Typography variant="body2" fontWeight="bold">
            Exercise {currentExerciseIndex + 1} of {totalExercises}
          </Typography>

          <Typography variant="body1" sx={{ mt: 1 }}>
            Set {client.current_set} of {currentExercise.sets}
          </Typography>
        </>
      ) : (
        <Typography>No exercises</Typography>
      )}

      <Box sx={{ mt: 2, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        {client.status === 'resting' && restTime > 0 ? (
          <Typography variant="h5" fontWeight="bold" color="warning.main" align="center">
            ⏱ REST: {Math.floor(restTime / 60)}:{String(restTime % 60).padStart(2, '0')}
          </Typography>
        ) : (
          <Typography variant="h6" fontWeight="bold" align="center" sx={{
            color: 
              client.status === 'ready' ? 'success.main' :
              client.status === 'in_progress' ? 'warning.main' :
              client.status === 'complete' ? 'text.secondary' : 'inherit'
          }}>
            {client.status === 'ready' && '✓ READY'}
            {client.status === 'in_progress' && '🔥 IN PROGRESS'}
            {client.status === 'complete' && '✅ COMPLETE'}
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default ClientQuadrant;
