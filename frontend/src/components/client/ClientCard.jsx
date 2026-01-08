
import React from 'react';
import { Card, CardContent, Typography, Box, Button, Chip } from '@mui/material';

const fitnessLevelColors = {
  Beginner: 'success',      // Green
  Intermediate: 'warning',  // Orange
  Advanced: 'error'         // Red
};

const ClientCard = ({ client, onEdit, onDeactivate }) => {
  const lastWorkout = client.last_workout_date 
    ? new Date(client.last_workout_date).toLocaleDateString()
    : 'Never trained';

  const truncatedGoals = client.goals.length > 100 
    ? client.goals.substring(0, 100) + '...'
    : client.goals;

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6">{client.name}</Typography>
          <Chip 
            label={client.fitness_level} 
            color={fitnessLevelColors[client.fitness_level]} 
            size="small" 
          />
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Age: {client.age}
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
          {truncatedGoals}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Last workout: {lastWorkout}
        </Typography>
      </CardContent>
      <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1 }}>
        <Button size="small" variant="outlined" onClick={() => onEdit(client)}>
          Edit
        </Button>
        <Button 
          size="small" 
          variant="contained" 
          color="error"
          onClick={() => onDeactivate(client)}
        >
          Deactivate
        </Button>
      </Box>
    </Card>
  );
};

export default ClientCard;
