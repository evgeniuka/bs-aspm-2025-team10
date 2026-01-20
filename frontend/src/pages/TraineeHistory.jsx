import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid, 
  Chip,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import TimerIcon from '@mui/icons-material/Timer';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Button from '@mui/material/Button';
import { clientService } from '../services/clientService';

const TraineeHistory = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await clientService.getTraineeSessions();
      setSessions(response.data?.sessions || []);
    } catch (err) {
      setError('Failed to load training history. Please check if the server is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getCompletionColor = (percentage) => {
    if (percentage === 100) return 'success';
    if (percentage >= 50) return 'warning';
    return 'error';
  };

  const getCompletionLabel = (percentage) => {
    if (percentage === 100) return '✓ Completed';
    if (percentage >= 50) return '⚠ Partial';
    return '✗ Incomplete';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header with Navigation Back */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Button 
            startIcon={<ArrowBackIcon />} 
            onClick={() => navigate('/trainee/dashboard')}
            sx={{ mb: 1 }}
          >
            Back to Dashboard
          </Button>
          <Typography variant="h4" fontWeight="bold">
            My Training History 💪
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View your past workouts and performance stats.
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Sessions Grid */}
      {sessions.length === 0 && !error ? (
        <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 3 }}>
          <Typography variant="h6" color="text.secondary">
            No workouts yet!
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Your training sessions will appear here once you complete them with your trainer.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {sessions.map((session) => (
            <Grid size={{ xs: 12, md: 6, lg: 4 }} key={session.session_id}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  borderRadius: 3,
                  transition: 'all 0.2s ease-in-out',
                  border: '1px solid #eee',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6,
                    borderColor: 'primary.main'
                  },
                }}
                onClick={() => navigate(`/trainee/session/${session.session_id}/details`)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" fontWeight="bold">
                      {new Date(session.started_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </Typography>
                    <Chip
                      label={getCompletionLabel(session.completion_percentage)}
                      color={getCompletionColor(session.completion_percentage)}
                      size="small"
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>

                  <Typography variant="subtitle1" color="primary.main" fontWeight="medium" gutterBottom>
                    {session.program_name}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Coach: {session.trainer_name}
                  </Typography>

                  <Divider sx={{ my: 2 }} />

                  <Grid container spacing={2}>
                    <Grid size={{ xs: 6 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TimerIcon fontSize="small" color="action" />
                        <Typography variant="body2" fontWeight="medium">
                          {session.duration_minutes} min
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <FitnessCenterIcon fontSize="small" color="action" />
                        <Typography variant="body2" fontWeight="medium">
                          {session.total_volume} kg
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  <Box sx={{ mt: 2, pt: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Progress: {session.exercises_completed} / {session.total_exercises} exercises
                    </Typography>
                    <Box 
                      sx={{ 
                        width: '100%', 
                        height: 6, 
                        bgcolor: '#eee', 
                        borderRadius: 3, 
                        mt: 0.5,
                        overflow: 'hidden' 
                      }}
                    >
                      <Box 
                        sx={{ 
                          width: `${session.completion_percentage}%`, 
                          height: '100%', 
                          bgcolor: getCompletionColor(session.completion_percentage) + '.main' 
                        }} 
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default TraineeHistory;