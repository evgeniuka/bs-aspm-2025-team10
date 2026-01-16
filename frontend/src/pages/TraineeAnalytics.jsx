// frontend/src/pages/TraineeAnalytics.jsx

import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  List,
  ListItem,
  ListItemText,
  Button,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import TimerIcon from '@mui/icons-material/Timer';
import EventIcon from '@mui/icons-material/Event';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate } from 'react-router-dom';
import { clientService } from '../services/clientService';

const TraineeAnalytics = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await clientService.getTraineeAnalytics(timeRange);
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  const MetricCard = ({ title, value, unit, icon }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value.toLocaleString()}
              <Typography variant="h6" component="span" color="text.secondary">
                {' '}{unit}
              </Typography>
            </Typography>
          </Box>
          <Box sx={{ color: 'primary.main' }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );

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

  if (!analytics) return null;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header with Back Button */}
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/trainee/dashboard')}
          sx={{ mb: 1 }}
        >
          Back to Dashboard
        </Button>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              My Progress 💪
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track your performance and personal records.
            </Typography>
          </Box>
          
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            size="small"
          >
            <ToggleButton value={30}>30 Days</ToggleButton>
            <ToggleButton value={60}>60 Days</ToggleButton>
            <ToggleButton value={90}>90 Days</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      {/* Overview Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <MetricCard
            title="Total Workouts"
            value={analytics.overview.total_sessions}
            unit=""
            icon={<EventIcon fontSize="large" />}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <MetricCard
            title="Total Volume Lifted"
            value={analytics.overview.total_volume_kg}
            unit="kg"
            icon={<FitnessCenterIcon fontSize="large" />}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <MetricCard
            title="Training Time"
            value={analytics.overview.total_time_minutes}
            unit="min"
            icon={<TimerIcon fontSize="large" />}
          />
        </Grid>
      </Grid>

      {/* Volume Progress Chart */}
      <Paper sx={{ p: 3, mb: 4, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom>
          Weekly Training Volume
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analytics.volume_over_time}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week_start" />
            <YAxis label={{ value: 'Volume (kg)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="volume"
              stroke="#1976d2"
              strokeWidth={3}
              name="Total Volume (kg)"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Personal Records */}
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <EmojiEventsIcon color="primary" />
          <Typography variant="h6">Personal Records (All Time)</Typography>
        </Box>
        {analytics.personal_records.length === 0 ? (
          <Alert severity="info">No personal records yet. Keep training!</Alert>
        ) : (
          <List>
            {analytics.personal_records.map((pr, index) => (
              <ListItem
                key={index}  
                sx={{
                  bgcolor: index === 0 ? 'primary.light' : 'background.paper',
                  mb: 1,
                  borderRadius: 5,
                  border: '5px solid',
                  borderColor: index === 0 ? 'primary.main' : '#eee',
                }}
              >
                <ListItemText
                  primary={
                    <Typography variant="h6" component="span">
                      {pr.exercise_name} - 
                    </Typography>
                  }
                  secondary={
                    <Typography variant="h5" component="span" color="primary">
                      {pr.max_weight} kg
                    </Typography>
                  }
                />
                {index === 0 && (
                  <EmojiEventsIcon sx={{ color: '#ffd700', fontSize: 40 }} />
                )}
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
};

export default TraineeAnalytics;
