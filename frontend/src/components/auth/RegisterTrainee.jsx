import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const RegisterTrainee = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [full_name, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const navigate = useNavigate();

  const validateForm = () => {
    if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
      setError('Please enter a valid email');
      return false;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (!full_name || full_name.trim().length < 2) {
      setError('Full name is required');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!validateForm()) return;

    setLoading(true);
    try {
      await axios.post('/api/auth/register', {
        email,
        password,
        full_name,
        role: 'trainee'
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      console.error('Registration error:', err);
      const message = err.response?.data?.error || 'Failed to register. Email may already be taken.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Container maxWidth="sm" sx={{ height: '100vh', display: 'flex', alignItems: 'center' }}>
        <Box sx={{ textAlign: 'center', p: 4, bgcolor: 'white', borderRadius: 2, boxShadow: 3 }}>
          <Typography variant="h5" color="success.main" gutterBottom>
            ✅ Registration Successful!
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Your account has been created.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Redirecting to login...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ height: '100vh', display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5' }}>
      <Grid container sx={{ height: '100%' }}>
        {/* Left panel — branding */}
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
            Join FitCoach Today
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary">
            Create your trainee account and start your fitness journey.
          </Typography>
        </Grid>

        {/* Right panel — registration form */}
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
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/login')}
              sx={{ alignSelf: 'flex-start', mb: 1 }}
            >
              Back to Login
            </Button>

            <Typography variant="h4" component="h1" fontWeight="bold" align="center" gutterBottom>
              Create Account
            </Typography>

            {error && <Alert severity="error">{error}</Alert>}

            <TextField
              label="Full Name"
              value={full_name}
              onChange={(e) => setFullName(e.target.value)}
              fullWidth
              required
              placeholder="John Doe"
            />

            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
              required
              placeholder="your.email@example.com"
            />

            <TextField
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              fullWidth
              required
              placeholder="••••••••"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              fullWidth
              required
              placeholder="••••••••"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)} edge="end">
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

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
              {loading ? 'Creating Account...' : 'Register'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default RegisterTrainee;