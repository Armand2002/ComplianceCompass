import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PatternProvider } from './context/PatternContext';

// Layouts
import MainLayout from './components/layout/MainLayout';

// Pagine
import LoginPage from './pages/auth/Login';
import RegisterPage from './pages/auth/Register';
import ForgotPasswordPage from './pages/auth/ForgotPassword';
import DashboardPage from './pages/dashboard/Dashboard';
import PatternListPage from './pages/patterns/PatternList';
import PatternDetailPage from './pages/patterns/PatternDetail';
import PatternCreatePage from './pages/patterns/PatternCreate';
import PatternEditPage from './pages/patterns/PatternEdit';
import SearchPage from './pages/search/SearchPage';
import ChatbotPage from './pages/chatbot/ChatbotPage';
import UserProfilePage from './pages/profile/UserProfile';
import NotFoundPage from './pages/NotFound';

// Componente per le rotte protette
import ProtectedRoute from './utils/ProtectedRoute';

import './styles/global.scss';

const App = () => {
  return (
    <AuthProvider>
      <PatternProvider>
        <Router>
          <Routes>
            {/* Rotte pubbliche */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            
            {/* Rotte protette con layout principale */}
            <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="patterns" element={<PatternListPage />} />
              <Route path="patterns/:id" element={<PatternDetailPage />} />
              <Route path="patterns/create" element={<PatternCreatePage />} />
              <Route path="patterns/:id/edit" element={<PatternEditPage />} />
              <Route path="search" element={<SearchPage />} />
              <Route path="chatbot" element={<ChatbotPage />} />
              <Route path="profile" element={<UserProfilePage />} />
            </Route>
            
            {/* Pagina 404 */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
      </PatternProvider>
    </AuthProvider>
  );
};

export default App;