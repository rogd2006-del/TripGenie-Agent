import axios from 'axios';

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  return '/api/v1';
};

const API_BASE_URL = getBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to inject JWT Bearer Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tripgenie_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Response interceptor with Retry Logic and Offline Server Handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Retry configuration
    if (config && !config._retryCount) {
      config._retryCount = 0;
    }

    const MAX_RETRIES = 2;
    if (config && config._retryCount < MAX_RETRIES && (error.code === 'ECONNABORTED' || !error.response || error.response.status >= 500)) {
      config._retryCount += 1;
      const delay = config._retryCount * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      return api(config);
    }

    // Standardize offline backend error
    if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED' || !error.response) {
      const offlineError = new Error('Backend server is offline.');
      offlineError.isOffline = true;
      offlineError.response = {
        data: {
          detail: 'Backend server is offline.',
          message: 'Backend server is offline.'
        },
        status: 503
      };
      return Promise.reject(offlineError);
    }

    return Promise.reject(error);
  }
);

export default api;
export { API_BASE_URL };
