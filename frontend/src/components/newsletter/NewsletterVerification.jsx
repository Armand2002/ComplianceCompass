// frontend/src/components/newsletter/NewsletterVerification.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { verifyNewsletterSubscription } from '../../services/newsletterService';
import LoadingSpinner from '../common/LoadingSpinner';
import AlertMessage from '../common/AlertMessage';
import './Newsletter.scss';

const NewsletterVerification = () => {
  const [status, setStatus] = useState('loading'); // loading, success, error
  const [message, setMessage] = useState('Verifica in corso...');
  const location = useLocation();
  const navigate = useNavigate();
  
  useEffect(() => {
    const verifySubscription = async () => {
      try {
        // Estrai email e token dalla query string
        const searchParams = new URLSearchParams(location.search);
        const email = searchParams.get('email');
        const token = searchParams.get('token');
        
        if (!email || !token) {
          setStatus('error');
          setMessage('Link di verifica non valido. Mancano parametri necessari.');
          return;
        }
        
        // Effettua la richiesta di verifica
        const response = await verifyNewsletterSubscription(email, token);
        
        // Gestisci la risposta
        setStatus('success');
        setMessage(response.message || 'Email verificata con successo! Ora sei iscritto alla newsletter.');
      } catch (error) {
        console.error('Errore durante la verifica:', error);
        setStatus('error');
        setMessage(error.message || 'Si è verificato un errore durante la verifica. Link non valido o scaduto.');
      }
    };
    
    verifySubscription();
  }, [location.search]);
  
  const goToHome = () => {
    navigate('/');
  };
  
  return (
    <div className="newsletter-verification-container">
      <div className="verification-card">
        <h2 className="verification-title">Verifica Iscrizione Newsletter</h2>
        
        {status === 'loading' && (
          <div className="verification-loading">
            <LoadingSpinner size="md" />
            <p className="mt-3">{message}</p>
          </div>
        )}
        
        {status === 'success' && (
          <div className="verification-success">
            <div className="verification-icon success">
              <i className="bi bi-check-circle-fill"></i>
            </div>
            <AlertMessage type="success" message={message} />
            <button onClick={goToHome} className="btn btn-primary mt-3">
              Torna alla home
            </button>
          </div>
        )}
        
        {status === 'error' && (
          <div className="verification-error">
            <div className="verification-icon error">
              <i className="bi bi-x-circle-fill"></i>
            </div>
            <AlertMessage type="danger" message={message} />
            <button onClick={goToHome} className="btn btn-primary mt-3">
              Torna alla home
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsletterVerification;