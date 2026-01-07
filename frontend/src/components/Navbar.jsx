import React from 'react';
import { Box, Toolbar, Typography, Button, Divider } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout(); 
    navigate('/login');
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'white', boxShadow: 1 }}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', px: 3 }}>
        <Typography variant="h6" component="div">
          FitCoach
        </Typography>
        {user && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body1">Hello, {user.full_name}</Typography>
            <Button
              variant="outlined"
              color="primary"
              onClick={handleLogout}
              sx={{ fontWeight: 'bold' }}
            >
              Logout
            </Button>
          </Box>
        )}
      </Toolbar>
      <Divider />
    </Box>
  );
};

export default Navbar; 