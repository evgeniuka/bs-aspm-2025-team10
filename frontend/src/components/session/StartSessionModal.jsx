import React, { useState, useEffect } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, 
  Checkbox, FormControlLabel, Grid, Box, Typography, Button, Select, MenuItem, Alert
} from '@mui/material';
import { clientService } from '../../services/clientService';
import { useNavigate } from 'react-router-dom';


const StartSessionModal = ({ open, onClose }) => {
  const [clients, setClients] = useState([]);
  const [selectedClients, setSelectedClients] = useState([]);
  const [clientPrograms, setClientPrograms] = useState({}); // { clientId: programId }
  const [clientProgramOptions, setClientProgramOptions] = useState({}); // { clientId: [programs] }
  const [loadingPrograms, setLoadingPrograms] = useState({});
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false); 
  
  const navigate = useNavigate();

  useEffect(() => {
    if (open) {
      fetchClients();
    }
  }, [open]);

  const fetchClients = async () => {
    try {
      const res = await clientService.getClients();
      setClients(res.data);
    } catch (err) {
      console.error('Failed to load clients:', err);
      setErrors(['Failed to load clients']);
    }
  };

  const fetchProgramsForClient = async (clientId) => {
    setLoadingPrograms(prev => ({ ...prev, [clientId]: true }));
    try {
      const res = await clientService.getProgramsByClient(clientId);
      setClientProgramOptions(prev => ({
        ...prev,
        [clientId]: res.data
      }));
    } catch (err) {
      console.error(`Failed to load programs for client ${clientId}:`, err);
      setClientProgramOptions(prev => ({ ...prev, [clientId]: [] }));
    } finally {
      setLoadingPrograms(prev => ({ ...prev, [clientId]: false }));
    }
  };

  const handleClientChange = (clientId, checked) => {
    if (checked) {
      setSelectedClients(prev => [...prev, clientId]);
      fetchProgramsForClient(clientId);
    } else {
      setSelectedClients(prev => prev.filter(id => id !== clientId));
      setClientPrograms(prev => {
        const newPrograms = { ...prev };
        delete newPrograms[clientId];
        return newPrograms;
      });
      setClientProgramOptions(prev => {
        const newOptions = { ...prev };
        delete newOptions[clientId];
        return newOptions;
      });
    }
  };

  const handleProgramChange = (clientId, programId) => {
    setClientPrograms(prev => ({
      ...prev,
      [clientId]: programId
    }));
  };

  const isFormValid = () => {
    return (
      selectedClients.length >= 1 &&
      selectedClients.length <= 4 &&
      selectedClients.every(clientId => clientPrograms[clientId])
    );
  };

  const handleSubmit = async () => {
    setLoading(true); 
    const data = {
      client_ids: selectedClients,
      program_ids: selectedClients.map(clientId => clientPrograms[clientId])
    };

    try {
      const res = await clientService.createSession(data);
      navigate(`/session/${res.data.session_id}`);
      alert(`Session started! ID: ${res.data.session_id}`);
      onClose();
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to start session';
      setErrors(Array.isArray(errorMsg) ? errorMsg : [errorMsg]);
    } finally {
      setLoading(false); 
    }
  };

  const selectedCount = selectedClients.length;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Start Group Training Session</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1" color={selectedCount >= 1 ? 'success.main' : 'error.main'}>
            Selected: {selectedCount}/4
          </Typography>
          {selectedCount < 1 && (
            <Alert severity="error" sx={{ mt: 1 }}>
              Select at least 1 client to start
            </Alert>
          )}
        </Box>

        <Grid container spacing={2}>
          {clients.map(client => (
            <Grid size={{ xs: 6 }} key={client.id}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={selectedClients.includes(client.id)}
                    onChange={(e) => handleClientChange(client.id, e.target.checked)}
                  />
                }
                label={client.name}
              />
            </Grid>
          ))}
        </Grid>

        {selectedClients.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Assign Programs</Typography>
            {selectedClients.map(clientId => {
              const client = clients.find(c => c.id === clientId);
              const programs = clientProgramOptions[clientId] || [];
              const hasPrograms = programs.length > 0;
              const isLoading = loadingPrograms[clientId];

              return (
                <Box key={clientId} sx={{ mb: 2 }}>
                  <Typography variant="body1" sx={{ mb: 1 }}>{client.name}</Typography>
                  {isLoading ? (
                    <Typography>Loading programs...</Typography>
                  ) : hasPrograms ? (
                    <Select
                      value={clientPrograms[clientId] || ''}
                      onChange={(e) => handleProgramChange(clientId, e.target.value)}
                      fullWidth
                    >
                      <MenuItem value="">-- Select Program --</MenuItem>
                      {programs.map(prog => (
                        <MenuItem key={prog.id} value={prog.id}>
                          {prog.name} ({prog.exercises.length} exercises)
                        </MenuItem>
                      ))}
                    </Select>
                  ) : (
                    <Alert severity="warning">
                      No programs available. Create one first.
                    </Alert>
                  )}
                </Box>
              );
            })}
          </Box>
        )}

        {errors.length > 0 && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errors.map((err, i) => <div key={i}>{err}</div>)}
          </Alert>
        )}

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={onClose}>Cancel</Button>
          {/* <Button 
            variant="contained" 
            color="success"
            onClick={handleSubmit}
            disabled={!isFormValid()}
          >
            Start Training
          </Button> */}

          <Button 
            variant="contained" 
            color="success"
            onClick={handleSubmit}
            disabled={!isFormValid() || loading} 
          >
            {loading ? 'Preparing session...' : 'Start Training'}
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default StartSessionModal;
