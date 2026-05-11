import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Button,
  ButtonGroup,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { clientService } from '../services/clientService';

const TrainerClientHistory = () => {
  const { clientId } = useParams();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [expandedSessionId, setExpandedSessionId] = useState(null);
  const [sessionDetails, setSessionDetails] = useState({});

  useEffect(() => {
    fetchSessions();
  }, [clientId]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await clientService.getClientSessions(clientId);
      setSessions(response.data.sessions);
    } catch (err) {
      setError('Failed to load training history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionDetails = async (sessionId) => {
    if (sessionDetails[sessionId]) return; 

    try {
      const response = await clientService.getSessionDetails(sessionId);
      setSessionDetails((prev) => ({
        ...prev,
        [sessionId]: response.data,
      }));
    } catch (err) {
      console.error('Failed to load session details:', err);
    }
  };

  const handleAccordionChange = (sessionId) => (event, isExpanded) => {
    setExpandedSessionId(isExpanded ? sessionId : null);
    if (isExpanded) {
      fetchSessionDetails(sessionId);
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
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Training History
        </Typography>
        <ButtonGroup variant="outlined" sx={{ mt: 2 }}>
          <Button
            variant={filter === 'all' ? 'contained' : 'outlined'}
            onClick={() => setFilter('all')}
          >
            All Sessions
          </Button>
          <Button
            variant={filter === '30days' ? 'contained' : 'outlined'}
            onClick={() => setFilter('30days')}
          >
            Last 30 Days
          </Button>
          <Button
            variant={filter === '3months' ? 'contained' : 'outlined'}
            onClick={() => setFilter('3months')}
          >
            Last 3 Months
          </Button>
        </ButtonGroup>
      </Box>

      {/* Sessions List */}
      {sessions.length === 0 ? (
        <Alert severity="info">
          No training sessions yet. Complete your first workout to see history!
        </Alert>
      ) : (
        sessions.map((session) => (
          <Accordion
            key={session.session_id}
            expanded={expandedSessionId === session.session_id}
            onChange={handleAccordionChange(session.session_id)}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', width: '100%', alignItems: 'center', gap: 2 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  {new Date(session.started_at).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {session.program_name}
                </Typography>
                <Chip
                  label={getCompletionLabel(session.completion_percentage)}
                  color={getCompletionColor(session.completion_percentage)}
                  size="small"
                />
                <Typography variant="body2" color="text.secondary">
                  {session.duration_minutes} min
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {session.total_volume} kg
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {sessionDetails[session.session_id] ? (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Exercise</TableCell>
                        <TableCell>Planned</TableCell>
                        <TableCell>Actual Performance</TableCell>
                        <TableCell align="right">Volume (kg)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sessionDetails[session.session_id].exercises.map((exercise) => (
                        <TableRow key={exercise.exercise_id}>
                          <TableCell>{exercise.exercise_name}</TableCell>
                          <TableCell>
                            {exercise.planned.sets} × {exercise.planned.reps} @ {exercise.planned.weight_kg}kg
                          </TableCell>
                          <TableCell>
                            {exercise.actual.length > 0
                              ? exercise.actual.map((set) => `${set.reps}`).join(', ') +
                                ` @ ${exercise.actual[0].weight_kg}kg`
                              : 'Not completed'}
                          </TableCell>
                          <TableCell align="right">{exercise.volume}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        ))
      )}
    </Container>
  );
};

export default TrainerClientHistory;
