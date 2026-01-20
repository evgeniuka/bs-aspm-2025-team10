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

// IMPORTANT: logout ONLY on 401/403, never on 404/500
clientApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;

    if (status === 401 || status === 403) {
      // Token is invalid/expired or not authorized
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');

      // Optional: also clear any user payload if you store it
      // localStorage.removeItem('user');
      // sessionStorage.removeItem('user');

      // Avoid infinite redirect loops if already on login
      const path = window.location?.pathname || '';
      if (!path.startsWith('/login')) {
        window.location.assign('/login');
      }
    }

    // For 404/500/etc: do NOT logout, just propagate error
    return Promise.reject(error);
  }
);

export const clientService = {
  getClients: () => clientApi.get('/clients'),
  createClient: (data) => clientApi.post('/clients', data),
  updateClient: (id, data) => clientApi.put(`/clients/${id}`, data),
  deactivateClient: (id) => clientApi.post(`/clients/${id}/deactivate`),

  // NOTE: if backend does not have /clients/my, this will 404 but will NOT logout anymore
  getMyClient: () => clientApi.get('/clients/my'),

  getExercises: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return clientApi.get(`/exercises${query ? `?${query}` : ''}`);
  },

  createProgram: (data) => clientApi.post('/programs', data),

  startSession: (data) => clientApi.post('/sessions', data),

  getProgramsByClient: (clientId) => clientApi.get(`/programs?client_id=${clientId}`),

  getSession: (sessionId) => {
    console.log(`Fetching session ${sessionId}`);
    return clientApi
      .get(`/sessions/${sessionId}`)
      .then((res) => {
        console.log('Session data received:', res.data);
        return res;
      })
      .catch((err) => {
        console.error('Error fetching session:', err);
        throw err;
      });
  },

  endSession: (sessionId) => clientApi.post(`/sessions/${sessionId}/end`),

  markSetComplete: (sessionId, data) => clientApi.post(`/sessions/${sessionId}/complete-set`, data),

  getClientSessions: (clientId) => clientApi.get(`/clients/${clientId}/sessions`),

  getSessionDetails: (sessionId) => clientApi.get(`/clients/sessions/${sessionId}/details`),

  getTraineeSessionDetails: (sessionId) => clientApi.get(`/trainee/sessions/${sessionId}/details`),

  getTraineeSessions: () => clientApi.get('/trainee/sessions'),

  getClientAnalytics: (clientId, days = 30) =>
    clientApi.get(`/clients/${clientId}/analytics?days=${days}`),

  getClientComparison: (clientId) =>
    clientApi.get(`/clients/${clientId}/analytics/comparison`),

  getTraineeAnalytics: (days = 30) =>
    clientApi.get(`/trainee/analytics?days=${days}`),

  // Use THIS in TraineeDashboard
  getTraineeActiveSession: () => clientApi.get('/trainee/session'),
};
