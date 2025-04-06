import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PatternProvider } from './context/PatternContext';
import { ToastProvider } from './components/common/Toast';

// Layouts
import MainLayout from './components/layout/MainLayout';

// Pagine pubbliche
import LoginPage from './pages/auth/Login';
import RegisterPage from './pages/auth/Register';
import ForgotPasswordPage from './pages/auth/ForgotPassword';
import HomePage from './pages/Homepage';
import AboutPage from './pages/AboutPage';
import NotFoundPage from './pages/NotFound';

// Pagine protette
import DashboardPage from './pages/dashboard/Dashboard';
import PatternListPage from './pages/patterns/PatternList';
import PatternDetailPage from './pages/patterns/PatternDetail';
import PatternCreatePage from './pages/patterns/PatternCreate';
import PatternEditPage from './pages/patterns/PatternEdit';
import SearchPage from './pages/search/SearchPage';
import ChatbotPage from './pages/chatbot/ChatbotPage';
import UserProfilePage from './pages/profile/UserProfile';

// Newsletter components
import NewsletterVerification from './components/newsletter/NewsletterVerification';
import ManageSubscription from './components/newsletter/ManageSubscription';

// Componente per le rotte protette
import ProtectedRoute from './utils/ProtectedRoute';

import './styles/global.scss';

const App = () => {
  return (
    <AuthProvider>
      <PatternProvider>
        <ToastProvider>
          <Router>
            <Routes>
              {/* Rotte pubbliche con layout principale */}
              <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/about" element={<AboutPage />} />
                
                {/* Rotte di autenticazione */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                
                {/* Rotte protette */}
                <Route element={<ProtectedRoute />}>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/patterns" element={<PatternListPage />} />
                  <Route path="/patterns/:id" element={<PatternDetailPage />} />
                  <Route path="/patterns/create" element={<PatternCreatePage />} />
                  <Route path="/patterns/:id/edit" element={<PatternEditPage />} />
                  <Route path="/search" element={<SearchPage />} />
                  <Route path="/chatbot" element={<ChatbotPage />} />
                  <Route path="/profile" element={<UserProfilePage />} />
                </Route>
                
                {/* Newsletter routes */}
                <Route path="/newsletter/verify" element={<NewsletterVerification />} />
                <Route path="/newsletter/manage" element={<ManageSubscription />} />
                
                {/* Pagina 404 */}
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </Router>
        </ToastProvider>
      </PatternProvider>
    </AuthProvider>
  );
};

export default App;