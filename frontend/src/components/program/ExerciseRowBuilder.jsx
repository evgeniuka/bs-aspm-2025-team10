import React from 'react';
import { Box, Typography, Chip, TextField, IconButton, InputAdornment } from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { ArrowUpward, ArrowDownward } from '@mui/icons-material';

const categoryColors = {
  upper_body: 'primary',
  lower_body: 'secondary',
  core: 'success',
  cardio: 'error',
  full_body: 'warning'
};

const ExerciseRowBuilder = ({exercise, onRemove, onChange, onMoveUp, onMoveDown, index, lastIdx}) => {  
  const handleFieldChange = (field, value) => {
    onChange({
      ...exercise,
      [field]: value
    });
  };

  return (
    <Box sx={{ p: 2, border: '1px solid #eee', borderRadius: 1, display: 'flex', gap: 1.5, alignItems: 'center' }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        <IconButton size="small" onClick={onMoveUp} disabled={index === 0}>
          <ArrowUpward fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={onMoveDown} disabled={index === lastIdx}>
          <ArrowDownward fontSize="small" />
        </IconButton>
      </Box>
      <Box sx={{ flex: 1 }}>
        <Typography variant="subtitle1" fontWeight="bold">{exercise.name}</Typography>
        <Chip 
          label={exercise.category.replace('_', ' ')} 
          size="small" 
          color={categoryColors[exercise.category]} 
          sx={{ mt: 0.5 }}
        />
      </Box>
      
      <TextField
        size="small"
        label="Sets"
        type="number"
        value={exercise.sets}
        onChange={(e) => handleFieldChange('sets', parseInt(e.target.value) || 1)}
        inputProps={{ min: 1, max: 10 }}
        sx={{ width: 70 }}
      />
      
      <TextField
        size="small"
        label="Reps"
        type="number"
        value={exercise.reps}
        onChange={(e) => handleFieldChange('reps', parseInt(e.target.value) || 1)}
        inputProps={{ min: 1, max: 50 }}
        sx={{ width: 70 }}
      />
      
      <TextField
        size="small"
        label="Weight (kg)"
        type="number"
        value={exercise.weight_kg}
        onChange={(e) => handleFieldChange('weight_kg', parseFloat(e.target.value) || 0)}
        inputProps={{ min: 0, max: 500, step: 0.5 }}
        sx={{ width: 100 }}
      />
      
      <TextField
        size="small"
        label="Rest (s)"
        type="number"
        value={exercise.rest_seconds}
        onChange={(e) => handleFieldChange('rest_seconds', parseInt(e.target.value) || 0)}
        inputProps={{ min: 0, max: 600 }}
        sx={{ width: 90 }}
      />
      
      <IconButton onClick={onRemove} size="small" color="error">
        <DeleteIcon />
      </IconButton>
    </Box>
  );
};

export default ExerciseRowBuilder;