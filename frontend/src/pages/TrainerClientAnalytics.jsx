
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import TimerIcon from '@mui/icons-material/Timer';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EventIcon from '@mui/icons-material/Event';
import { clientService } from '../services/clientService';

const TrainerClientAnalytics = () => {
  const { clientId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState(30); 

  useEffect(() => {
    fetchAnalytics();
    fetchComparison();
  }, [clientId, timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await clientService.getClientAnalytics(clientId, timeRange);
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchComparison = async () => {
    try {
      const response = await clientService.getClientComparison(clientId);
      setComparison(response.data);
    } catch (err) {
      console.error('Failed to load comparison:', err);
    }
  };

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  const MetricCard = ({ title, value, unit, icon, change }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ mb: 1 }}>
              {value.toLocaleString()}
              <Typography variant="h6" component="span" color="text.secondary">
                {' '}{unit}
              </Typography>
            </Typography>
            {change !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {change >= 0 ? (
                  <TrendingUpIcon fontSize="small" color="success" />
                ) : (
                  <TrendingDownIcon fontSize="small" color="error" />
                )}
                <Typography
                  variant="body2"
                  color={change >= 0 ? 'success.main' : 'error.main'}
                >
                  {change > 0 ? '+' : ''}{change}% vs last week
                </Typography>
              </Box>
            )}
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
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">Client Progress Analytics</Typography>
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

      {/* Overview Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Sessions"
            value={analytics.overview.total_sessions}
            unit=""
            icon={<EventIcon fontSize="large" />}
            change={comparison?.changes.session_change_percent}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Volume"
            value={analytics.overview.total_volume_kg}
            unit="kg"
            icon={<FitnessCenterIcon fontSize="large" />}
            change={comparison?.changes.volume_change_percent}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Training Time"
            value={analytics.overview.total_time_minutes}
            unit="min"
            icon={<TimerIcon fontSize="large" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Completion Rate"
            value={analytics.overview.avg_completion_rate}
            unit="%"
            icon={<CheckCircleIcon fontSize="large" />}
          />
        </Grid>
      </Grid>

      {/* Volume Over Time Chart */}
      <Paper sx={{ p: 3, mb: 4 }}>
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
              strokeWidth={2}
              name="Total Volume (kg)"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Exercise Performance */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Top Exercises by Volume
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={analytics.exercise_performance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="exercise_name" />
            <YAxis label={{ value: 'Volume (kg)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="total_volume" fill="#2196f3" name="Total Volume (kg)" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Weekly Frequency */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Training Frequency (Sessions per Week)
        </Typography>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={analytics.weekly_frequency}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="sessions" fill="#4caf50" name="Sessions" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Strength Progression */}
      {Object.keys(analytics.strength_progression).length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Strength Progression (Max Weight)
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                type="category"
                allowDuplicatedCategory={false}
              />
              <YAxis label={{ value: 'Weight (kg)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              {Object.entries(analytics.strength_progression).map(([exercise, data], index) => {
                const colors = ['#f44336', '#2196f3', '#4caf50', '#ff9800'];
                return (
                  <Line
                    key={exercise}
                    data={data}
                    type="monotone"
                    dataKey="max_weight"
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    name={exercise}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}
    </Container>
  );
};

export default TrainerClientAnalytics;
