import axios from 'axios';

// Crea un'istanza di axios con configurazione di base
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor per aggiungere il token di autenticazione alle richieste
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor per gestire gli errori di risposta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Se l'errore è 401 (Unauthorized) e non abbiamo già provato a rinnovare il token
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Tenta di rinnovare il token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // Se non c'è un refresh token, reindirizza al login
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        const response = await axios.post('/api/auth/refresh', {
          refresh_token: refreshToken,
        });
        
        if (response.data.access_token) {
          // Salva il nuovo token
          localStorage.setItem('access_token', response.data.access_token);
          
          // Aggiorna l'header della richiesta originale
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          
          // Riprova la richiesta originale
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Se il refresh fallisce, reindirizza al login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;