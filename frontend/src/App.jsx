import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/auth/Login';
import ProtectedRoute from './components/auth/ProtectedRoute';
import TrainerDashboard from './pages/TrainerDashboard';
import TraineeDashboard from './pages/TraineeDashboard';
import ProgramBuilder from './pages/ProgramBuilder';
import SessionView from './pages/SessionView';
import SplitScreenView from './pages/SplitScreenView';
import Navbar from './components/Navbar';
import SessionSummary from './pages/SessionSummary'; 
import TrainerClientHistory from './pages/TrainerClientHistory';
import TraineeHistory from './pages/TraineeHistory'
import TrainerClientAnalytics from './pages/TrainerClientAnalytics';
import TraineeAnalytics from './pages/TraineeAnalytics';
import TraineeSessionDetails from './pages/TraineeSessionDetails';
import TraineeLiveSession from './pages/trainee/TraineeLiveSession';


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
        
        <Route
          path="/trainer/program/new"
          element={
            <ProtectedRoute requiredRole="trainer">
              <ProgramBuilder />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
        <Route path="/session/:id" element={<SplitScreenView />} />
        <Route path="/session/:id/summary" element={<SessionSummary />} />
        <Route path="/trainer/clients/:clientId/history" element={<TrainerClientHistory />} />
        <Route path="/trainee/history" element={<TraineeHistory />} />
        <Route path="/trainer/clients/:clientId/analytics" element={<TrainerClientAnalytics />} />
        <Route path="/trainee/analytics" element={<TraineeAnalytics />} />
        <Route path="/trainee/session/:sessionId/details" element={<TraineeSessionDetails />} />
        <Route path="/trainee/live-session" element={<TraineeLiveSession />} />

      </Routes>
    </>
  );
}


export default App;