import React from 'react';
import { Card, CardContent, Typography, Box, Button, Chip, Divider } from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

const fitnessLevelColors = {
  Beginner: 'success',
  Intermediate: 'warning',
  Advanced: 'error'
};

const ClientCard = ({ client, onEdit, onDeactivate, onViewHistory, onViewAnalytics }) => {
  const lastWorkout = client.last_workout_date 
    ? new Date(client.last_workout_date).toLocaleDateString()
    : 'Never trained';

  const truncatedGoals = client.goals.length > 100 
    ? client.goals.substring(0, 100) + '...'
    : client.goals;

  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        border: '2px solid #000',
        borderRadius: 2,
        boxShadow: '4px 4px 0px #bcbcbc',
        bgcolor: 'white',
        transition: 'all 0.2s',
        '&:hover': {
          boxShadow: '6px 6px 0px #6f6f6f',
          transform: 'translate(-2px, -2px)'
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1, p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight="bold" sx={{ color: '#000' }}>
            {client.name}
          </Typography>
          <Chip 
            label={client.fitness_level} 
            color={fitnessLevelColors[client.fitness_level]} 
            size="small"
            sx={{ 
              fontWeight: 'bold',
              border: '1px solid #000'
            }}
          />
        </Box>

        <Divider sx={{ mb: 2, borderColor: '#000', borderWidth: 1 }} />

        {/* Details */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1, color: '#666', fontWeight: 500 }}>
            AGE: <span style={{ color: '#000', fontWeight: 'bold' }}>{client.age}</span>
          </Typography>
          
          <Typography variant="body2" sx={{ mb: 1.5, color: '#333', lineHeight: 1.5 }}>
            {truncatedGoals}
          </Typography>
          
          <Box 
            sx={{ 
              p: 1.5, 
              bgcolor: '#f5f5f5', 
              border: '1px solid #000',
              borderRadius: 1,
              mt: 2
            }}
          >
            <Typography variant="caption" sx={{ color: '#666', fontWeight: 500 }}>
              LAST WORKOUT
            </Typography>
            <Typography variant="body2" fontWeight="bold" sx={{ color: '#000' }}>
              {lastWorkout}
            </Typography>
          </Box>
        </Box>
      </CardContent>

      <Divider sx={{ borderColor: '#000', borderWidth: 1 }} />

      {/* Action Buttons */}
      <Box sx={{ p: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button 
          size="small" 
          variant="outlined"
          startIcon={<EditIcon />}
          onClick={() => onEdit(client)}
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
              bgcolor: '#f5f5f5'
            }
          }}
        >
          Edit
        </Button>
        
        <Button 
          size="small" 
          variant="outlined"
          startIcon={<AnalyticsIcon />}
          onClick={() => onViewAnalytics(client.id)}
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
              bgcolor: '#f5f5f5'
            }
          }}
        >
          Analytics
        </Button>
        
        <Button 
          size="small" 
          variant="outlined"
          startIcon={<HistoryIcon />}
          onClick={() => onViewHistory(client.id)}
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
              bgcolor: '#f5f5f5'
            }
          }}
        >
          History
        </Button>
        
        <Button 
          size="small" 
          variant="contained"
          startIcon={<DeleteIcon />}
          onClick={() => onDeactivate(client)}
          sx={{
            bgcolor: '#424242',
            color: 'white',
            fontWeight: 'bold',
            textTransform: 'uppercase',
            fontSize: '0.7rem',
            border: '2px solid #000',
            '&:hover': {
              bgcolor: '#333',
              border: '2px solid #000'
            }
          }}
        >
          Deactivate
        </Button>
      </Box>
    </Card>
  );
};

export default ClientCard;
