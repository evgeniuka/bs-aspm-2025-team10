import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import TimerIcon from '@mui/icons-material/Timer';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import { clientService } from '../services/clientService';

const TraineeSessionDetails = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSessionDetails();
  }, [sessionId]);

  const fetchSessionDetails = async () => {
    try {
      setLoading(true);
 
      const response = await clientService.getTraineeSessionDetails(sessionId);
      setDetails(response.data);
    } catch (err) {
      setError('Failed to load session details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/trainee/history')}
          sx={{ mt: 2 }}
        >
          Back to History
        </Button>
      </Container>
    );
  }

  if (!details) return null;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/trainee/history')}
          sx={{ mb: 2 }}
        >
          Back to History
        </Button>

        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Workout Details
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 3, mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body1" color="text.secondary">
              Date:
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {new Date(details.started_at).toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric',
              })}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimerIcon fontSize="small" color="action" />
            <Typography variant="body1" fontWeight="medium">
              {details.duration_minutes} min
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Program Info */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3, bgcolor: '#f8f9fa' }}>
        <Typography variant="h6" gutterBottom>
          {details.program_name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Coach: {details.trainer_name}
        </Typography>
      </Paper>

      {/* Exercises Table */}
      <TableContainer component={Paper} sx={{ borderRadius: 3 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: 'primary.light' }}>
              <TableCell><strong>Exercise</strong></TableCell>
              <TableCell><strong>Planned</strong></TableCell>
              <TableCell><strong>Actual Performance</strong></TableCell>
              <TableCell align="right"><strong>Volume (kg)</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {details.exercises.map((exercise, index) => {
              const completed = exercise.actual.length > 0;
              return (
                <TableRow 
                  key={exercise.exercise_id}
                  sx={{ 
                    bgcolor: index % 2 === 0 ? 'background.paper' : '#f8f9fa',
                    '&:hover': { bgcolor: '#e3f2fd' }
                  }}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body1" fontWeight="medium">
                        {exercise.exercise_name}
                      </Typography>
                      {completed && (
                        <Chip label="✓" size="small" color="success" />
                      )}
                    </Box>
                  </TableCell>
                  
                  <TableCell>
                    <Typography variant="body2">
                      {exercise.planned.sets} × {exercise.planned.reps} @ {exercise.planned.weight_kg}kg
                    </Typography>
                  </TableCell>
                  
                  <TableCell>
                    {completed ? (
                      <Typography variant="body2">
                        {exercise.actual.map((set) => set.reps).join(', ')} reps
                        <br />
                        @ {exercise.actual[0].weight_kg}kg
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Not completed
                      </Typography>
                    )}
                  </TableCell>
                  
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                      <FitnessCenterIcon fontSize="small" color="action" />
                      <Typography variant="body1" fontWeight="bold">
                        {exercise.volume}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default TraineeSessionDetails;
