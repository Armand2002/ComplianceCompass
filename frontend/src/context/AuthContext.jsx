import React, { createContext, useState, useEffect, useContext } from 'react';
import AuthService from '../api/authService';

// Creazione del contesto
export const AuthContext = createContext();

// Crea un hook personalizzato per usare il contesto
export const useAuth = () => useContext(AuthContext);

/**
 * Provider per il contesto di autenticazione
 * @param {Object} props - Props del componente
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Controlla se l'utente è già autenticato al caricamento dell'app
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        if (AuthService.isAuthenticated()) {
          // Ottieni le informazioni dell'utente corrente
          const userData = await AuthService.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        }
      } catch (err) {
        console.error('Errore nel controllo dello stato di autenticazione:', err);
        // Se c'è un errore, rimuovi i token per sicurezza
        AuthService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  /**
   * Effettua il login dell'utente
   * @param {string} email - Email dell'utente
   * @param {string} password - Password dell'utente
   */
  const login = async (email, password) => {
    setIsLoading(true);
    setError(null);
    try {
      // Effettua il login
      await AuthService.login(email, password);
      
      // Ottieni le informazioni dell'utente
      const userData = await AuthService.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante il login');
      return { success: false, error: err.response?.data?.detail || 'Errore durante il login' };
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Registra un nuovo utente
   * @param {Object} userData - Dati dell'utente
   */
  const register = async (userData) => {
    setIsLoading(true);
    setError(null);
    try {
      await AuthService.register(userData);
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante la registrazione');
      return { success: false, error: err.response?.data?.detail || 'Errore durante la registrazione' };
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Effettua il logout dell'utente
   */
  const logout = () => {
    AuthService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  /**
   * Aggiorna i dati dell'utente corrente
   */
  const updateUserData = async () => {
    if (isAuthenticated) {
      try {
        const userData = await AuthService.getCurrentUser();
        setUser(userData);
      } catch (err) {
        console.error('Errore nell\'aggiornamento dei dati dell\'utente:', err);
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        updateUserData,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;