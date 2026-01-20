import React from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

const SessionSummary = () => {
  const { id: sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const summary = location.state?.summary;

  if (!summary) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h5">No summary data available</Typography>
        <Button onClick={() => navigate('/trainer/dashboard')} sx={{ mt: 2 }}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Training Session Summary
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Session #{sessionId}
          </Typography>
          <Typography variant="h6" sx={{ mt: 2 }}>
            Duration: {formatDuration(summary.duration_minutes)}
          </Typography>
        </Box>

        {/* Client Cards */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {summary.clients.map((client) => {
            const isComplete = client.completion_percentage === 100;
            const isPartial = client.completion_percentage >= 50 && client.completion_percentage < 100;

            return (
              <Card key={client.client_id} elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6" fontWeight="bold">
                      {client.client_name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {isComplete ? (
                        <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                      ) : (
                        <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                      )}
                      <Typography
                        variant="body1"
                        fontWeight="bold"
                        sx={{
                          color: isComplete
                            ? 'success.main'
                            : isPartial
                            ? 'warning.main'
                            : 'error.main'
                        }}
                      >
                        {client.completion_percentage}%
                      </Typography>
                    </Box>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={client.completion_percentage}
                    sx={{
                      height: 8,
                      borderRadius: 1,
                      mb: 2,
                      '& .MuiLinearProgress-bar': {
                        bgcolor: isComplete
                          ? 'success.main'
                          : isPartial
                          ? 'warning.main'
                          : 'error.main'
                      }
                    }}
                  />

                  <Typography variant="body2" color="text.secondary">
                    Exercises: {client.exercises_completed}/{client.total_exercises}
                  </Typography>
                </CardContent>
              </Card>
            );
          })}
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/trainer/dashboard')}
            sx={{ minWidth: 150 }}
          >
            Back to Dashboard
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/session/new')}
            sx={{ minWidth: 150 }}
          >
            Start New Session
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default SessionSummary;
