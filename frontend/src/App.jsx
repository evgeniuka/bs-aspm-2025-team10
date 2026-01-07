import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/auth/Login';
import ProtectedRoute from './components/auth/ProtectedRoute';
import TrainerDashboard from './pages/TrainerDashboard';
// import TraineeDashboard from './pages/TraineeDashboard';
import Navbar from './components/Navbar';

// const TrainerDashboard = () => <div style={{ padding: '20px' }}>🏋️ Trainer Dashboard</div>;
const TraineeDashboard = () => <div style={{ padding: '20px' }}>🏃 Trainee Dashboard</div>;


function App() {
  return (
    <>
      <Navbar /> 
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/trainer/dashboard"
          element={
            <ProtectedRoute requiredRole="trainer">
              <TrainerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trainee/dashboard"
          element={
            <ProtectedRoute requiredRole="trainee">
              <TraineeDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  );
}


export default App;