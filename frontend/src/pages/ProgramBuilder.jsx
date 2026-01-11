import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, TextField, FormControl, InputLabel, Select, MenuItem, Button, Grid, Alert, Snackbar } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { clientService } from '../services/clientService';
import ExerciseLibrary from '../components/exercise/ExerciseLibrary';
import ExerciseRowBuilder from '../components/program/ExerciseRowBuilder';
import ConfirmDialog from '../components/client/ConfirmDialog'; 


const ProgramBuilder = () => {
  const { user } = useAuth();
  const [clients, setClients] = useState([]);
  const [programData, setProgramData] = useState({
    name: '',
    client_id: '',
    notes: ''
  });
  const [exercises, setExercises] = useState([]);
  const [openLibrary, setOpenLibrary] = useState(false);
  const [errors, setErrors] = useState([]);
  const [exerciseToRemove, setExerciseToRemove] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    const isDirty = 
      programData.name.trim() !== '' ||
      programData.client_id !== '' ||
      programData.notes.trim() !== '' ||
      exercises.length > 0;
    setHasUnsavedChanges(isDirty);
  }, [programData, exercises]);

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = ''; 
        return '';          
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges]);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const res = await clientService.getClients();
        setClients(res.data);
      } catch (err) {
        console.error('Failed to load clients:', err);
        setErrors(['Failed to load clients']);
      }
    };
    fetchClients();
  }, []);

  const handleAddExercise = (selectedExercises) => {
    const newExercises = selectedExercises.map(ex => ({
      exercise_id: ex.id,
      name: ex.name,
      category: ex.category,
      sets: 1,
      reps: 1,
      weight_kg: 0,
      rest_seconds: 60,
      notes: ''
    }));
    setExercises(prev => [...prev, ...newExercises]);
    setOpenLibrary(false);
  };

  const handleUpdateExercise = (updatedExercise) => {
    setExercises(prev =>
      prev.map(ex =>
        ex.exercise_id === updatedExercise.exercise_id ? updatedExercise : ex
      )
    );
  };

  const handleRemoveExercise = (exerciseId) => {
    setExerciseToRemove(exerciseId);
  };

  const isFormValid = () => {
    return (
      programData.name.trim().length >= 3 &&
      programData.client_id &&
      exercises.length >= 5 &&
      exercises.length <= 20
    );
  };

  const handleSubmit = async () => {
    const data = {
      ...programData,
      exercises: exercises.map((ex, idx) => ({
        exercise_id: ex.exercise_id,
        sets: ex.sets,
        reps: ex.reps,
        weight_kg: ex.weight_kg,
        rest_seconds: ex.rest_seconds,
        notes: ex.notes,
        order: idx
      }))
    };

    try {
      const response = await clientService.createProgram(data);
            setSnackbar({ 
        open: true, 
        message: `Program "${programData.name}" created successfully!`, 
        severity: 'success' 
      });
      
      setTimeout(() => {
        navigate('/trainer/dashboard');
      }, 1000);
      
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to save program';
      setErrors([errorMsg]);
      setSnackbar({ 
        open: true, 
        message: errorMsg, 
        severity: 'error' 
      });
    }
  };


  const handleMoveUp = (index) => {
    if (index === 0) return;
    const newExercises = [...exercises];
    [newExercises[index - 1], newExercises[index]] = [newExercises[index], newExercises[index - 1]];
    setExercises(newExercises);
  };

  const handleMoveDown = (index) => {
    if (index === exercises.length - 1) return;
    const newExercises = [...exercises];
    [newExercises[index], newExercises[index + 1]] = [newExercises[index + 1], newExercises[index]];
    setExercises(newExercises);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Create Workout Program</Typography>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={!isFormValid()}
        >
          Save Program
        </Button>
      </Box>

      {errors.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {errors.join(', ')}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Left sidebar - Program details */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
            <TextField
              fullWidth
              label="Program Name *"
              value={programData.name}
              onChange={(e) => setProgramData({...programData, name: e.target.value})}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Client *</InputLabel>
              <Select
                value={programData.client_id}
                onChange={(e) => setProgramData({...programData, client_id: e.target.value})}
                label="Select Client *"
              >
                <MenuItem value="">-- Select Client --</MenuItem>
                {clients.map(client => (
                  <MenuItem key={client.id} value={client.id}>
                    {client.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={4}
              value={programData.notes}
              onChange={(e) => setProgramData({...programData, notes: e.target.value})}
            />
          </Box>
        </Grid>

        {/* Right area - Exercise list */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Exercises ({exercises.length}/20)</Typography>
            <Button 
              variant="outlined" 
              onClick={() => setOpenLibrary(true)}
              disabled={exercises.length >= 20}
            >
              Add Exercise
            </Button>
          </Box>
          
          {exercises.length === 0 ? (
            <Typography color="text.secondary">
              Add at least 5 exercises to create a program
            </Typography>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
             {exercises.map((ex, idx) => (
              <ExerciseRowBuilder
                key={ex.exercise_id}
                exercise={ex}
                index={idx}
                lastIdx={exercises.length - 1}
                onChange={handleUpdateExercise}
                onRemove={() => handleRemoveExercise(ex.exercise_id)}
                onMoveUp={() => handleMoveUp(idx)}
                onMoveDown={() => handleMoveDown(idx)}
              />
            ))}
            </Box>
          )}
          
          {exercises.length < 5 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Add at least 5 exercises to save the program
            </Alert>
          )}
          
          {exercises.length >= 20 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Maximum 20 exercises reached
            </Alert>
          )}
        </Grid>
      </Grid>

      <ExerciseLibrary
        open={openLibrary}
        onClose={() => setOpenLibrary(false)}
        onAddExercise={handleAddExercise}
      />

      <ConfirmDialog
        open={!!exerciseToRemove}
        onClose={() => setExerciseToRemove(null)}
        onConfirm={() => {
          setExercises(prev => prev.filter(ex => ex.exercise_id !== exerciseToRemove));
          setExerciseToRemove(null);
        }}
        title="Remove Exercise"
        content="Are you sure you want to remove this exercise from the program?"
      />  
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
        
    </Container>
  );
};

export default ProgramBuilder;