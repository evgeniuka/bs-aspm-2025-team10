// src/pages/TraineeDashboard.jsx
import React from 'react';
import { useAuth } from '../context/AuthContext';

const TraineeDashboard = () => {
  const { user } = useAuth();

  return (
    <div style={{ padding: '20px' }}>
      <h1>🏃 Welcome, {user?.full_name || 'Trainee'}!</h1>
      <p>This is your trainee dashboard.</p>
    </div>
  );
};

export default TraineeDashboard;