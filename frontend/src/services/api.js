import axios from 'axios';
import { toast } from 'react-toastify';

// Centralized axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    console.error('API Error:', error);
    
    // Common error handling
    if (error.response) {
      // Handle 401 (unauthorized)
      if (error.response.status === 401) {
        console.log('Token expired or unauthorized');
      }
      
      // Handle server errors
      else if (error.response.status >= 500) {
        // Only show toast if react-toastify is available
        if (typeof toast === 'function') {
          toast.error('Server error. Please try again later.');
        }
        
        console.error('Server error details:', error.response.data);
      }
    } else if (error.request) {
      // Request was made but no response received
      if (typeof toast === 'function') {
        toast.error('Cannot reach the server.');
      }
    } else {
      // Error in setting up the request
      if (typeof toast === 'function') {
        toast.error('An error occurred during the request.');
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;