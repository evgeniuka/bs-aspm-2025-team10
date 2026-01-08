
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { clientService } from '../services/clientService';

const TraineeDashboard = () => {
  const { user } = useAuth();
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchClient = async () => {
      try {
        const response = await clientService.getMyClient(); 
        setClient(response.data);
      } catch (err) {
        setError('Failed to load your profile');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchClient();
    }
  }, [user]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!client) return <div>No training profile assigned yet.</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>🏃 Welcome, {user?.full_name}!</h1>
      <h2>Your Profile:</h2>
      <p><strong>Name:</strong> {client.name}</p>
      <p><strong>Age:</strong> {client.age}</p>
      <p><strong>Fitness Level:</strong> {client.fitness_level}</p>
      <p><strong>Goals:</strong> {client.goals}</p>
    </div>
  );
};

export default TraineeDashboard;