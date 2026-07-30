import api from './api';

export const authService = {
  async register(full_name, email, password) {
    const res = await api.post('/auth/register', { full_name, email, password });
    if (res.data.access_token) {
      localStorage.setItem('tripgenie_token', res.data.access_token);
    }
    return res.data;
  },

  async login(email, password) {
    const res = await api.post('/auth/login', { email, password });
    if (res.data.access_token) {
      localStorage.setItem('tripgenie_token', res.data.access_token);
    }
    return res.data;
  },

  async getProfile() {
    const res = await api.get('/auth/profile');
    return res.data;
  },

  logout() {
    localStorage.removeItem('tripgenie_token');
  }
};
