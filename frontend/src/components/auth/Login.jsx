import React, { useState } from 'react';
import { Box, Container, Grid, TextField, Button, Typography, FormControlLabel, Checkbox, Link,  InputAdornment,
  IconButton,} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios'; 
import { useAuth } from '../../context/AuthContext';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true); 
  setError('');

    try {
      const response = await axios.post('/api/auth/login', {
        email,
        password,
      });

      const data = response.data; 

      localStorage.setItem('token', data.token);
      setUser(data.user);

      if (data.user.role === 'trainer') {
        navigate('/trainer/dashboard');
      } else {
        navigate('/trainee/dashboard');
      }


    } catch (err) {
      console.error('Login error:', err); 
      setError('Invalid email or password'); 
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ height: '100vh', display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5' }}>
      <Grid container sx={{ height: '100%' }}>
        {/* left panel */}
        <Grid size={{ xs: 12, md: 6 }} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', bgcolor: '#eeeeee', p: 4 }}>
          <Box
            sx={{
              width: 150,
              height: 150,
              bgcolor: 'white',
              border: '2px solid #bdbdbd',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            <Typography variant="h1">⚡️</Typography>
          </Box>
          <Typography variant="h4" align="center" fontWeight="bold" color="text.secondary" gutterBottom>
            Transform Your Fitness Journey
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary">
            Connect. Train. Achieve.
          </Typography>
        </Grid>

        {/* right panel */}
        <Grid size={{ xs: 12, md: 6 }} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
          <Box
            sx={{
              width: '100%',
              maxWidth: 400,
              p: 4,
              bgcolor: 'white',
              borderRadius: 2,
              boxShadow: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <Typography variant="h4" component="h1" fontWeight="bold" align="center" gutterBottom>
              Sign in to FitCoach
            </Typography>
           

            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
              required
              placeholder="your.email@example.com"
              error={!!error}
              helperText={error}
              variant="outlined"
              size="small"
            />


            <TextField
              label="Password "
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              fullWidth
              required
              placeholder="••••••••"
              variant="outlined"
              size="small"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />


            {/* Sign in button */}
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleSubmit}
              disabled={loading}
              sx={{
                mt: 2, 
                py: 1.5, 
                fontWeight: 'bold',
                backgroundColor: 'black',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'gray',
                },
              }}
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>

            <Typography variant="body2" align="center" sx={{ mt: 2 }}>
              New client?{' '}
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/register/trainee')}
                sx={{ textDecoration: 'underline' }}
              >
                Register here
              </Link>
            </Typography>
        </Box>
      </Grid>
    </Grid>
  </Container>
  );
};

export default Login;
