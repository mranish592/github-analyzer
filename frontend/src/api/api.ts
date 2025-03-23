// api.js
import axios from 'axios';

const baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api'; // Default URL

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    // Add other common headers here
  },
});

// Add request interceptors
api.interceptors.request.use(
  (config) => {
    // Modify request config (e.g., add authorization token)
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptors
api.interceptors.response.use(
  (response) => {
    // Modify response data or handle successful responses
    return response;
  },
  (error) => {
    // Handle errors (e.g., show error messages, redirect to login)
    return Promise.reject(error);
  }
);

export default api;