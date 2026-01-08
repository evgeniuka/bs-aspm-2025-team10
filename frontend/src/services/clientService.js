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
  }
};

