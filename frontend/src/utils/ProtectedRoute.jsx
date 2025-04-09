import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext'; // Importa solo il contesto

// Modifica da useAuth a useContext(AuthContext)
const ProtectedRoute = () => {
  // Usa React.useContext invece di useAuth
  const auth = React.useContext(AuthContext);
  
  // Verifica isAuthenticated dal contesto
  return auth.isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;