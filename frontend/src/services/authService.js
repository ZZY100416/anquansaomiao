import api from './api';

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    return response;
  },

  register: async (username, password, email) => {
    return await api.post('/auth/register', { username, password, email });
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: async () => {
    return await api.get('/auth/me');
  },
};

export const useAuth = () => {
  return {
    isAuthenticated: () => {
      return !!localStorage.getItem('token');
    },
    getUser: () => {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    },
  };
};

