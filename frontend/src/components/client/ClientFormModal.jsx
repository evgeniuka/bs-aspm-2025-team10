import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem,
  Button, Alert
} from '@mui/material';

const ClientFormModal = ({ open, onClose, onSubmit, initialData = null }) => {
  const isEdit = !!initialData;
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    fitness_level: 'Beginner',
    goals: '',
    user_email: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        age: initialData.age || '',
        fitness_level: initialData.fitness_level || 'Beginner',
        goals: initialData.goals || '',
        user_email: initialData.user_email || '' 
      });
    } else {
      setFormData({
        name: '',
        age: '',
        fitness_level: 'Beginner',
        goals: '',
        user_email: ''
      });
    }
  }, [initialData]); 

  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.name || formData.name.length < 2 || formData.name.length > 50) {
      setError('Name must be 2-50 characters');
      return;
    }
    if (!/^[a-zA-Z\s-]+$/.test(formData.name)) {
      setError('Name can only contain letters, spaces, and hyphens');
      return;
    }
    const ageNum = parseInt(formData.age, 10);
    if (isNaN(ageNum) || ageNum < 16 || ageNum > 100) {
      setError('Age must be between 16 and 100');
      return;
    }
    if (!formData.goals || formData.goals.length < 10) {
      setError('Goals must be at least 10 characters');
      return;
    }


    const submitData = {
      ...formData,
      age: ageNum
    };


    if (isEdit && initialData) {
      submitData.id = initialData.id; 
    }

    onSubmit(submitData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEdit ? 'Edit Client' : 'Add New Client'}</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField
            margin="dense"
            name="name"
            label="Name *"
            fullWidth
            value={formData.name}
            onChange={handleChange}
            required
          />
          <TextField
            margin="dense"
            name="age"
            label="Age *"
            type="number"
            fullWidth
            value={formData.age}
            onChange={handleChange}
            required
            inputProps={{ min: 16, max: 100 }}
          />
          <TextField
            margin="dense"
            name="user_email"
            label="Client Email (optional)"
            fullWidth
            placeholder="maya@fitcoach.com"
            value={formData.user_email}
            onChange={handleChange}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Fitness Level *</InputLabel>
            <Select
              name="fitness_level"
              value={formData.fitness_level}
              onChange={handleChange}
              label="Fitness Level *"
            >
              <MenuItem value="Beginner">Beginner</MenuItem>
              <MenuItem value="Intermediate">Intermediate</MenuItem>
              <MenuItem value="Advanced">Advanced</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            name="goals"
            label="Goals *"
            multiline
            rows={4}
            fullWidth
            value={formData.goals}
            onChange={handleChange}
            required
          />
        </form>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={onClose}
          variant="outlined"
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
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="outlined"
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
          {isEdit ? 'Save Changes' : 'Create Client'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ClientFormModal;
