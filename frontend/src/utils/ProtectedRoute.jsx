import React, { useContext } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

/**
 * Componente per le rotte protette
 * Reindirizza al login se l'utente non è autenticato
 */
const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useContext(AuthContext);
  const location = useLocation();

  // Mostra un loader durante il controllo dell'autenticazione
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento...</p>
      </div>
    );
  }

  // Reindirizza al login se l'utente non è autenticato
  if (!isAuthenticated) {
    // Salva l'URL corrente per reindirizzare l'utente dopo il login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Renderizza le route figlie tramite Outlet
  return <Outlet />;
};

export default ProtectedRoute;