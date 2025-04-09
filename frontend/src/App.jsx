import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PatternProvider } from './context/PatternContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layouts
import MainLayout from './components/layout/MainLayout';
import ProtectedRoute from './utils/ProtectedRoute';

// Pagine pubbliche
import LoginPage from './pages/auth/Login';
import RegisterPage from './pages/auth/Register';
import ForgotPasswordPage from './pages/auth/ForgotPassword';
import HomePage from './pages/Homepage';
import AboutPage from './pages/AboutPage';
import NotFoundPage from './pages/NotFound';
import GDPRPage from './pages/gdpr/GDPRPage';
import PrivacyByDesignPage from './pages/privacy-by-design/PrivacyByDesignPage';

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

import './styles/global.scss';

const App = () => {
  return (
    <AuthProvider>
      <PatternProvider>
        <Router>
          <Routes>
            <Route element={<MainLayout />}>
              {/* Rotte pubbliche */}
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/patterns" element={<PatternListPage />} />
              <Route path="/patterns/:id" element={<PatternDetailPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/gdpr" element={<GDPRPage />} />
              <Route path="/privacy-by-design" element={<PrivacyByDesignPage />} />
              
              {/* Rotte newsletter (pubbliche) */}
              <Route path="/newsletter/verify" element={<NewsletterVerification />} />
              <Route path="/newsletter/manage" element={<ManageSubscription />} />
              
              {/* Rotte di autenticazione */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              
              {/* Rotte protette */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/patterns/create" element={<PatternCreatePage />} />
                <Route path="/patterns/:id/edit" element={<PatternEditPage />} />
                <Route path="/chatbot" element={<ChatbotPage />} />
                <Route path="/profile" element={<UserProfilePage />} />
              </Route>
              
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Router>
        <ToastContainer position="top-right" autoClose={5000} />
      </PatternProvider>
    </AuthProvider>
  );
};

export default App;