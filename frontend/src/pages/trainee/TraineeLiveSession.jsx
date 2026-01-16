import React, { useState, useEffect } from 'react';
import { Box, Typography, LinearProgress, Paper, Chip, Divider, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { clientService } from '../../services/clientService';
import { socketService } from '../../services/socket';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PendingIcon from '@mui/icons-material/Pending';

const TraineeLiveSession = () => {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch active session
    const fetchSession = async () => {
      try {
        console.log('📡 Fetching active session...');
        
        const response = await clientService.getTraineeActiveSession();
        
        console.log('✅ Session data received:', response.data);
        setSession(response.data);
        
        // Join WebSocket room
        const socket = socketService.connect();
        
        socket.on('connect', () => {
          console.log('✅ WebSocket connected for live session');
          
          socketService.emit('trainee_join_session', {
            session_id: response.data.session_id,
            trainee_id: response.data.client_id
          });
        });
        
      } catch (error) {
        console.error('❌ Error fetching session:', error);
        setError(error.response?.data?.error || 'Failed to load session');
        
        if (error.response?.status === 404) {
          setTimeout(() => {
            navigate('/trainee/dashboard');
          }, 2000);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchSession();

    // Listen for WebSocket updates
    socketService.on('session_update', (data) => {
      console.log('🔄 Session update received:', data);
      
      if (session && data.client_id === session.client_id) {
        setSession(prev => ({
          ...prev,
          current_exercise: data.updated_client_data?.current_exercise || prev.current_exercise,
          sets_completed: data.updated_client_data?.sets_completed || prev.sets_completed,
          status: data.updated_client_data?.status || prev.status,
          rest_time_remaining: data.updated_client_data?.rest_time_remaining
        }));
      }
    });

    socketService.on('session_ended', (data) => {
      console.log('🛑 Session ended:', data);
      alert('Your training session has ended');
      navigate('/trainee/dashboard');
    });

    // Cleanup
    return () => {
      console.log('🧹 TraineeLiveSession unmounting');
      socketService.off('session_update');
      socketService.off('session_ended');
    };
  }, [navigate]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography color="error" variant="h6">{error}</Typography>
        <Typography variant="body2" sx={{ mt: 2 }}>
          Redirecting to dashboard...
        </Typography>
      </Box>
    );
  }

  if (!session) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography>No active session</Typography>
      </Box>
    );
  }

  const { current_exercise, sets_completed, status, total_exercises, exercises_completed, rest_time_remaining } = session;

  const totalSets = current_exercise?.sets || 0;
  const completedSets = sets_completed?.length || 0;
  const progressPercentage = totalSets > 0 ? (completedSets / totalSets) * 100 : 0;

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      bgcolor: '#f5f5f5', 
      p: 3 
    }}>
      {/* Header */}
      <Paper sx={{ 
        p: 3, 
        mb: 3, 
        bgcolor: '#000', 
        color: 'white',
        border: '2px solid #000'
      }}>
        <Typography variant="h4" fontWeight="bold">
          Live Training Session 🏋️
        </Typography>
        <Typography variant="body1" sx={{ mt: 1 }}>
          Trainer: {session.trainer_name} | Program: {session.program_name}
        </Typography>
      </Paper>

      {/* Overall Progress */}
      <Paper sx={{ p: 3, mb: 3, border: '2px solid #000' }}>
        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
          Overall Progress
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography>Exercises Completed:</Typography>
          <Typography fontWeight="bold">{exercises_completed}/{total_exercises}</Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={(exercises_completed / total_exercises) * 100} 
          sx={{ height: 10, borderRadius: 5 }}
        />
      </Paper>

      {/* Current Exercise */}
      {current_exercise && status !== 'completed' ? (
        <Paper sx={{ p: 3, border: '2px solid #000', boxShadow: '4px 4px 0px #000' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" fontWeight="bold">
              {current_exercise.name}
            </Typography>
            <Chip 
              label={status === 'resting' ? '⏱️ RESTING' : '💪 WORKING'}
              color={status === 'resting' ? 'warning' : 'success'}
              sx={{ fontWeight: 'bold' }}
            />
          </Box>

          <Divider sx={{ mb: 2, borderColor: '#000' }} />

          <Box sx={{ mb: 3 }}>
            <Typography variant="body1">
              <strong>Target:</strong> {current_exercise.sets} sets × {current_exercise.reps} reps @ {current_exercise.weight_kg}kg
            </Typography>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography fontWeight="bold">Sets Progress:</Typography>
              <Typography fontWeight="bold">{completedSets}/{totalSets}</Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progressPercentage} 
              sx={{ 
                height: 16, 
                borderRadius: 8,
                border: '2px solid #000',
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#10b981'
                }
              }}
            />
          </Box>

          {status === 'resting' && rest_time_remaining > 0 && (
            <Paper sx={{ 
              p: 2, 
              mb: 3, 
              bgcolor: '#fbbf24', 
              border: '2px solid #000',
              textAlign: 'center'
            }}>
              <Typography variant="h4" fontWeight="bold">
                ⏱️ Rest: {Math.floor(rest_time_remaining / 60)}:{(rest_time_remaining % 60).toString().padStart(2, '0')}
              </Typography>
              <Typography variant="body2">Take a break, you earned it!</Typography>
            </Paper>
          )}

          <Box>
            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
              Sets Breakdown
            </Typography>
            {Array.from({ length: totalSets }, (_, i) => {
              const setData = sets_completed?.find(s => s.set_number === i + 1);
              const isCompleted = !!setData;

              return (
                <Box 
                  key={i}
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    p: 2, 
                    mb: 1, 
                    border: '1px solid #000',
                    borderRadius: 1,
                    bgcolor: isCompleted ? '#d1fae5' : '#f5f5f5'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isCompleted ? (
                      <CheckCircleIcon sx={{ color: '#10b981' }} />
                    ) : (
                      <PendingIcon sx={{ color: '#999' }} />
                    )}
                    <Typography fontWeight="bold">Set {i + 1}</Typography>
                  </Box>

                  {isCompleted ? (
                    <Typography>
                      {setData.reps_completed} reps @ {setData.weight_kg}kg
                    </Typography>
                  ) : (
                    <Typography sx={{ color: '#999' }}>Waiting...</Typography>
                  )}
                </Box>
              );
            })}
          </Box>
        </Paper>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center', border: '2px solid #10b981', bgcolor: '#d1fae5' }}>
          <Typography variant="h4" fontWeight="bold" sx={{ color: '#10b981', mb: 2 }}>
            🎉 Workout Complete!
          </Typography>
          <Typography variant="body1">
            Great job! You've completed all exercises in this program.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default TraineeLiveSession;
