import axios from 'axios';

const clientApi = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

clientApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const clientService = {
  getClients: () => clientApi.get('/clients'),
  createClient: (data) => clientApi.post('/clients', data),
  updateClient: (id, data) => clientApi.put(`/clients/${id}`, data),
  deactivateClient: (id) => clientApi.post(`/clients/${id}/deactivate`),
  getMyClient: () => clientApi.get('/clients/my'), 
  getExercises: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return clientApi.get(`/exercises${query ? '?' + query : ''}`);
  },
  createProgram: (data) => {
    return clientApi.post('/programs', data);
  },
  startSession: (data) => {
    return clientApi.post('/sessions', data);
  },
  getProgramsByClient: (clientId) => {
    return clientApi.get(`/programs?client_id=${clientId}`);
  },
  getSession: (sessionId) => {
    console.log(`Fetching session ${sessionId}`); 
    return clientApi.get(`/sessions/${sessionId}`).then(res => {
      console.log('Session data received:', res.data); 
      return res;
    }).catch(err => {
      console.error('Error fetching session:', err); 
      throw err;
    });
  },
  endSession: (sessionId) => {
    return clientApi.post(`/sessions/${sessionId}/end`);
  },
  markSetComplete: (sessionId, data) => {
    return clientApi.post(`/sessions/${sessionId}/complete-set`, data);
  },
};