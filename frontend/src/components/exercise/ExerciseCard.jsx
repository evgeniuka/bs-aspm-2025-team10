import React from 'react';
import { Card, CardContent, Typography, Chip, Box } from '@mui/material';

const categoryColors = {
  upper_body: 'primary',
  lower_body: 'secondary',
  core: 'success',
  cardio: 'error',
  full_body: 'warning'
};

const difficultyColors = {
  beginner: 'success',
  intermediate: 'warning',
  advanced: 'error'
};

const equipmentIcons = {
  bodyweight: '🏋️',
  barbell: '🏋️‍♂️',
  dumbbell: '💪',
  machine: '⚙️',
  cable: '🔗',
  kettlebell: '🔔',
  other: '🔄'
};

const ExerciseCard = ({ exercise, onAdd }) => {
  const truncatedDesc = exercise.description.length > 120
    ? exercise.description.substring(0, 120) + '...'
    : exercise.description;

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6">{exercise.name}</Typography>
          <Typography variant="h4">{equipmentIcons[exercise.equipment] || '❓'}</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
          <Chip label={exercise.category.replace('_', ' ')} size="small" color={categoryColors[exercise.category]} />
          <Chip label={exercise.difficulty} size="small" color={difficultyColors[exercise.difficulty]} />
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-line' }}>
          {truncatedDesc}
        </Typography>
      </CardContent>
      <Box sx={{ p: 2, pt: 0 }}>
        <button onClick={() => onAdd(exercise)}>Add</button>
      </Box>
    </Card>
  );
};

export default ExerciseCard;