import React from 'react';
import { useAuth } from '../context/AuthContext';

const TrainerDashboard = () => {
  const { user } = useAuth();

  return (
    <div style={{ padding: '20px' }}>
      <h1>🏋️ Welcome, {user?.full_name || 'Trainer'}!</h1>
      <p>This is your trainer dashboard.</p>
    </div>
  );
};

export default TrainerDashboard;