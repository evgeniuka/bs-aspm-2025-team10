import React, { useState, useEffect } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, 
  TextField, Chip, Select, MenuItem, InputLabel, FormControl,
  Grid, Box, Typography, Button, IconButton, Divider
} from '@mui/material';
import ExerciseCard from './ExerciseCard';
import { clientService } from '../../services/clientService';
import CloseIcon from '@mui/icons-material/Close'; 

const categories = [
  { value: '', label: 'All' },
  { value: 'upper_body', label: 'Upper Body' },
  { value: 'lower_body', label: 'Lower Body' },
  { value: 'core', label: 'Core' },
  { value: 'cardio', label: 'Cardio' },
  { value: 'full_body', label: 'Full Body' }
];

const difficulties = [
  { value: '', label: 'All' },
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' }
];

const ExerciseLibrary = ({ open, onClose, onAddExercise }) => {
  const [exercises, setExercises] = useState([]);
  const [filteredExercises, setFilteredExercises] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [selectedExercises, setSelectedExercises] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      setLoading(true);
      clientService.getExercises()
        .then(res => {
          setExercises(res.data);
          setFilteredExercises(res.data);
        })
        .catch(err => console.error('Error fetching exercises:', err))
        .finally(() => setLoading(false));
    }
  }, [open]);

  useEffect(() => {
    let result = exercises;
    if (search) {
      const term = search.toLowerCase();
      result = result.filter(e => e.name.toLowerCase().includes(term));
    }
    if (category) result = result.filter(e => e.category === category);
    if (difficulty) result = result.filter(e => e.difficulty === difficulty);
    setFilteredExercises(result);
  }, [exercises, search, category, difficulty]);

  const handleAdd = (exercise) => {
    if (!selectedExercises.some(ex => ex.id === exercise.id)) {
      setSelectedExercises(prev => [...prev, exercise]);
    }
  };

  const handleRemove = (exerciseId) => {
    setSelectedExercises(prev => prev.filter(e => e.id !== exerciseId));
  };

  const handleConfirm = () => {
    onAddExercise(selectedExercises);
    setSelectedExercises([]);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth scroll="paper">
      <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        Exercise Library
        <IconButton onClick={onClose}><CloseIcon /></IconButton>
      </DialogTitle>
      
      <Divider />

      <DialogContent sx={{ display: 'flex', p: 0, height: '70vh' }}>
        <Box sx={{ 
          width: 300, 
          borderRight: '1px solid #ddd', 
          display: 'flex', 
          flexDirection: 'column',
          bgcolor: '#eaeaea' 
        }}>
          <Box sx={{ p: 2, flexGrow: 1, overflowY: 'auto' }}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Selected ({selectedExercises.length})
            </Typography>
            
            {selectedExercises.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No exercises selected yet.
              </Typography>
            ) : (
              selectedExercises.map(ex => (
                <Box 
                  key={ex.id} 
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    p: 1, mb: 1, 
                    bgcolor: 'white',
                    border: '1px solid #030303', 
                    borderRadius: 1 
                  }}
                >
                  <Typography variant="body2" noWrap sx={{ maxWidth: '200px' }}>
                    {ex.name}
                  </Typography>
                  <IconButton size="small" onClick={() => handleRemove(ex.id)}>
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Box>
              ))
            )}
          </Box>

          <Box sx={{ p: 2, borderTop: '1px solid #ddd', bgcolor: 'white' }}>
            <Button 
              fullWidth
              variant="outlined" 
              disabled={selectedExercises.length === 0}
              onClick={handleConfirm}
              sx={{
            color: '#000',
            borderColor: '#000',
            borderWidth: 2,
            fontWeight: 'bold',
            textTransform: 'uppercase',
            fontSize: '0.7rem',
            '&:hover': {
              borderColor: '#000',
              borderWidth: 2,
              bgcolor: '#737373'
            }
          }}
            >
              Confirm ({selectedExercises.length})
            </Button>
          </Box>
        </Box>

        <Box sx={{ flexGrow: 1, p: 3, overflowY: 'auto' }}>
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              placeholder="Search exercises..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              sx={{ mb: 2 }}
            />
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {categories.map(cat => (
                  <Chip
                    key={cat.value}
                    label={cat.label}
                    variant={category === cat.value ? 'filled' : 'outlined'}
                    onClick={() => setCategory(cat.value)}
                    color="primary"
                    size="small"
                  />
                ))}
              </Box>
              
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Difficulty</InputLabel>
                <Select 
                  value={difficulty} 
                  onChange={(e) => setDifficulty(e.target.value)} 
                  label="Difficulty"
                >
                  {difficulties.map(diff => (
                    <MenuItem key={diff.value} value={diff.value}>{diff.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </Box>

          {loading ? (
            <Typography>Loading exercises...</Typography>
          ) : filteredExercises.length === 0 ? (
            <Typography>No exercises found. Try different filters.</Typography>
          ) : (
            <Grid container spacing={2}>
              {filteredExercises.map(ex => (
                <Grid item xs={12} sm={6} md={4} key={ex.id}>
                  <ExerciseCard exercise={ex} onAdd={handleAdd} />
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default ExerciseLibrary;