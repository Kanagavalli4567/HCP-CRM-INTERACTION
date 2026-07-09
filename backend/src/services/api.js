// frontend/src/services/api.js
import axios from 'axios';

// Vite uses import.meta.env for environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

console.log('🔗 API URL:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('📤 Request:', config.method.toUpperCase(), config.url);
    console.log('🔗 Full URL:', config.baseURL + config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('📥 Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Error Details:');
    console.error('   Message:', error.message);
    console.error('   Code:', error.code);
    console.error('   URL:', error.config?.url);
    console.error('   BaseURL:', error.config?.baseURL);
    
    if (error.code === 'ERR_NETWORK') {
      console.error('❌ Backend server is not running or unreachable!');
      console.error('   Make sure to start the backend:');
      console.error('   cd backend && uvicorn app.main:app --reload');
    }
    return Promise.reject(error);
  }
);

export default api;