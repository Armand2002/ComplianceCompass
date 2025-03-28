import React, { useState, useContext, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { FaEnvelope, FaLock, FaExclamationTriangle } from 'react-icons/fa';
import { AuthContext } from '../../context/AuthContext';

// Schema di validazione per Formik
const LoginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Email non valida')
    .required('Email obbligatoria'),
  password: Yup.string()
    .required('Password obbligatoria'),
});

const LoginPage = () => {
  const { login, isAuthenticated, isLoading, error } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Stato per mostrare eventuali errori di form
  const [formError, setFormError] = useState('');

  // Reindirizza se l'utente è già autenticato
  useEffect(() => {
    if (isAuthenticated) {
      // Reindirizza alla pagina richiesta o alla dashboard
      const { from } = location.state || { from: { pathname: '/dashboard' } };
      navigate(from);
    }
  }, [isAuthenticated, navigate, location]);

  // Gestisce la sottomissione del form
  const handleSubmit = async (values, { setSubmitting }) => {
    setFormError('');
    
    try {
      const result = await login(values.email, values.password);
      
      if (!result.success) {
        setFormError(result.error || 'Errore durante il login');
      }
    } catch (err) {
      setFormError('Si è verificato un errore durante il login. Riprova più tardi.');
      console.error('Errore durante il login:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-logo">
          <img src="/assets/images/logo.png" alt="Compliance Compass" />
          <h1>Compliance Compass</h1>
        </div>
        
        <div className="auth-box">
          <div className="auth-header">
            <h2>Accedi</h2>
            <p>Inserisci le tue credenziali per accedere</p>
          </div>
          
          {(formError || error) && (
            <div className="auth-error">
              <FaExclamationTriangle />
              <span>{formError || error}</span>
            </div>
          )}
          
          <Formik
            initialValues={{ email: '', password: '' }}
            validationSchema={LoginSchema}
            onSubmit={handleSubmit}
          >
            {({ isSubmitting, touched, errors }) => (
              <Form className="auth-form">
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <div className={`input-with-icon ${touched.email && errors.email ? 'has-error' : ''}`}>
                    <FaEnvelope className="input-icon" />
                    <Field type="email" id="email" name="email" placeholder="La tua email" />
                  </div>
                  <ErrorMessage name="email" component="div" className="error-message" />
                </div>
                
                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <div className={`input-with-icon ${touched.password && errors.password ? 'has-error' : ''}`}>
                    <FaLock className="input-icon" />
                    <Field type="password" id="password" name="password" placeholder="La tua password" />
                  </div>
                  <ErrorMessage name="password" component="div" className="error-message" />
                </div>
                
                <div className="forgot-password">
                  <Link to="/forgot-password">Password dimenticata?</Link>
                </div>
                
                <button 
                  type="submit" 
                  className="auth-button" 
                  disabled={isSubmitting || isLoading}
                >
                  {isSubmitting || isLoading ? 'Accesso in corso...' : 'Accedi'}
                </button>
              </Form>
            )}
          </Formik>
          
          <div className="auth-footer">
            <p>Non hai un account? <Link to="/register">Registrati</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;