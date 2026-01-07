import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (email, password, rememberMe = false) => {
    const response = await api.post('/auth/login', { email, password });
    const { token, user } = response.data;

    if (rememberMe) {
      localStorage.setItem('token', token);
    } else {
      sessionStorage.setItem('token', token);
    }

    return { token, user };
  },

 logout: async () => {
  try {
    await api.post('/auth/logout'); 
  } catch (error) {
    console.error('Logout API error:', error);
  } finally {
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
  }
},

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token') || !!sessionStorage.getItem('token');
  },

  getToken: () => {
    return localStorage.getItem('token') || sessionStorage.getItem('token');
  },

  getUserRole: () => {
    const token = authService.getToken();
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role;
      } catch (e) {
        console.error('Invalid JWT token');
        return null;
      }
    }
    return null;
  },
};