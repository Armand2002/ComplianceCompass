import api from './axios';

/**
 * Servizio per la gestione dell'autenticazione
 */
const AuthService = {
  /**
   * Effettua il login dell'utente
   * @param {string} email - Email dell'utente
   * @param {string} password - Password dell'utente
   * @returns {Promise} - Promise con i dati di risposta
   */
  login: async (email, password) => {
    // L'API richiede un formato specifico (FormData) per OAuth2
    const formData = new FormData();
    formData.append('username', email); // L'API usa 'username' ma accetta email
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // Salva i token nel localStorage
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token || ''); // Potrebbe non essere presente
    }
    
    return response.data;
  },
  
  /**
   * Registra un nuovo utente
   * @param {Object} userData - Dati dell'utente
   * @returns {Promise} - Promise con i dati di risposta
   */
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  /**
   * Effettua il logout dell'utente
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  
  /**
   * Ottiene le informazioni dell'utente corrente
   * @returns {Promise} - Promise con i dati dell'utente
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  /**
   * Cambia la password dell'utente
   * @param {string} currentPassword - Password attuale
   * @param {string} newPassword - Nuova password
   * @param {string} confirmPassword - Conferma nuova password
   * @returns {Promise} - Promise con i dati di risposta
   */
  changePassword: async (currentPassword, newPassword, confirmPassword) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },
  
  /**
   * Richiede il reset della password
   * @param {string} email - Email dell'utente
   * @returns {Promise} - Promise con i dati di risposta
   */
  requestPasswordReset: async (email) => {
    const response = await api.post('/auth/request-password-reset', { email });
    return response.data;
  },
  
  /**
   * Resetta la password con un token
   * @param {string} token - Token di reset
   * @param {string} newPassword - Nuova password
   * @param {string} confirmPassword - Conferma nuova password
   * @returns {Promise} - Promise con i dati di risposta
   */
  resetPassword: async (token, newPassword, confirmPassword) => {
    const response = await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },
  
  /**
   * Verifica se l'utente è autenticato
   * @returns {boolean} - True se l'utente è autenticato
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

export default AuthService;