import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert
} from '@mui/material';
import { format } from 'date-fns';

const EndSessionDialog = ({ 
  open, 
  onClose, 
  onConfirm, 
  session, 
  loading 
}) => {
  if (!session) return null;
  
  const durationMinutes = Math.floor(
    (new Date() - new Date(session.created_at)) / 60000
  );
  
  const allCompleted = session.clients.every(
    client => client.current_exercise_index >= client.program.exercises.length - 1
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>End Training Session?</DialogTitle>
      
      <DialogContent>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Are you sure you want to end this session for all {session.clients.length} clients?
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Session duration: {durationMinutes} minutes
        </Typography>
        
        {/* Completion Summary */}
        <Box sx={{ mb: 2 }}>
          {session.clients.map(client => {
            const totalExercises = client.program.exercises.length;
            const completedExercises = client.completed_exercises?.length || 0;
            const percentage = Math.round((completedExercises / totalExercises) * 100);
            const isComplete = completedExercises >= totalExercises;
            
            return (
              <Box key={client.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">
                  {isComplete ? '✓' : '⚠'} {client.name}
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                  {completedExercises}/{totalExercises} ({percentage}%)
                </Typography>
              </Box>
            );
          })}
        </Box>
        
        {/* Warning if incomplete */}
        {!allCompleted && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Some clients haven't finished. End anyway?
          </Alert>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={onConfirm} 
          color="error" 
          variant="contained"
          disabled={loading}
          startIcon={<span>⏹</span>}
        >
          {loading ? 'Saving...' : 'Yes, End Session'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EndSessionDialog;