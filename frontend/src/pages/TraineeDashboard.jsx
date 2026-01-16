import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Paper, 
  Card, 
  CardContent, 
  Divider,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import PersonIcon from '@mui/icons-material/Person';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import { useAuth } from '../context/AuthContext';
import { clientService } from '../services/clientService';
import { socketService } from '../services/socket';

const TraineeDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [client, setClient] = useState(null);
  const [lastSession, setLastSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      if (user?.role === 'trainer') {
        setLoading(false);
        return;
      }

      try {

        const clientResponse = await clientService.getMyClient();
        console.log('📊 Client data:', clientResponse.data);
        console.log('🆔 Client ID:', clientResponse.data.id);
        setClient(clientResponse.data);


        const sessionsResponse = await clientService.getTraineeSessions();
        if (sessionsResponse.data.sessions && sessionsResponse.data.sessions.length > 0) {
          setLastSession(sessionsResponse.data.sessions[0]);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to load your profile');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);


  useEffect(() => {
    console.log('🔄 TraineeDashboard mounted');
    
    if (!user || !user.id) {
      console.warn('⚠️ No user found, cannot connect to WebSocket');
      return;
    }
    
    const checkActiveSession = async () => {
      try {
        const response = await clientService.get('/trainee/session');
        
        if (response.data && response.data.session_id) {
          console.log('✅ Active session found, redirecting to live session');
          navigate('/trainee/live-session');
          return true;
        }
      } catch (error) {
        console.log('ℹ️ No active session');
      }
      return false;
    };

    const setupWebSocket = async () => {
      try {
        const clientResponse = await clientService.getMyClient();
        const clientId = clientResponse.data.id;
        
        console.log('🔌 Connecting to WebSocket for client:', clientId);
        const socket = socketService.connect();
        
        socket.on('connect', () => {
          console.log('✅ WebSocket connected, now emitting trainee_connect');
          socketService.emit('trainee_connect', { trainee_id: clientId });
        });
        
        socketService.on('session_started', (data) => {
          console.log('🔔 Session started notification:', data);
          setNotification('Your trainer started a training session!');
          setTimeout(() => {
            navigate('/trainee/live-session');
          }, 2000);
        });
      } catch (error) {
        console.error('❌ Failed to setup WebSocket:', error);
      }
    };

    const init = async () => {
      const hasActiveSession = await checkActiveSession();
      if (!hasActiveSession) {
        await setupWebSocket();
      }
    };

    init();


    return () => {
      console.log('🧹 TraineeDashboard unmounting');
      socketService.off('session_started')

    };
  }, [navigate, user]);





  const getRelativeTime = (dateString) => {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
      <CircularProgress />
    </Box>
  );

  if (!client) return (
    <Container sx={{ mt: 4 }}>
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography>No training profile assigned yet. Please contact your trainer.</Typography>
      </Paper>
    </Container>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          🏃 Welcome back, {user?.full_name}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ready for your next breakthrough?
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Profile Summary Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', borderRadius: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">My Profile</Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2" gutterBottom>
                <strong>Level:</strong> {client.fitness_level}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Age:</strong> {client.age}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Goals:</strong> {client.goals}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Card */}
        <Grid item xs={12} md={8}>
          <Card
            sx={{ 
              height: '100%',
              cursor: 'pointer',
              borderRadius: 3,
              transition: 'all 0.2s',
              '&:hover': { 
                boxShadow: 6, 
                transform: 'translateY(-2px)',
                bgcolor: '#f8f9fa'
              }
            }}
            onClick={() => navigate('/trainee/analytics')}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AnalyticsIcon sx={{ mr: 1, color: 'success.main', fontSize: 32 }} />
                <Typography variant="h6">My Progress</Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CalendarTodayIcon fontSize="small" color="action" />
                    <Typography variant="caption" color="text.secondary">
                      Last Workout
                    </Typography>
                  </Box>
                  <Typography variant="h6" fontWeight="bold">
                    {lastSession ? getRelativeTime(lastSession.started_at) : 'No workouts yet'}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <FitnessCenterIcon fontSize="small" color="action" />
                    <Typography variant="caption" color="text.secondary">
                      Last Session Volume
                    </Typography>
                  </Box>
                  <Typography variant="h6" fontWeight="bold">
                    {lastSession ? `${lastSession.total_volume} kg` : '-- kg'}
                  </Typography>
                </Grid>

                {lastSession && (
                  <>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Duration
                      </Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {lastSession.duration_minutes} min
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Completion
                      </Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {lastSession.completion_percentage}%
                      </Typography>
                    </Grid>
                  </>
                )}
              </Grid>

              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #eee' }}>
                <Typography 
                  variant="body2" 
                  color="primary.main" 
                  fontWeight="bold"
                  sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                >
                  Click to view detailed analytics & PRs →
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Training History Card */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{ 
              cursor: 'pointer', 
              height: '100%',
              borderRadius: 3,
              '&:hover': { boxShadow: 6, transform: 'translateY(-2px)' },
              transition: 'all 0.2s'
            }}
            onClick={() => navigate('/trainee/history')}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <HistoryIcon color="primary" sx={{ fontSize: 48 }} />
                <Box>
                  <Typography variant="h6">Training History</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Review all past workouts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Motivation Card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%', borderRadius: 3, bgcolor: 'primary.main', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}>
                <Typography variant="h5" fontWeight="bold" gutterBottom>
                  🔥 Keep Pushing!
                </Typography>
                <Typography variant="body1">
                  "The only bad workout is the one that didn't happen."
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Notification Snackbar */}
      <Snackbar
        open={!!notification}
        autoHideDuration={6000}
        onClose={() => setNotification('')}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="success" sx={{ width: '100%' }}>
          {notification}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TraineeDashboard;
