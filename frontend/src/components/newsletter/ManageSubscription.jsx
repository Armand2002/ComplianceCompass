// frontend/src/components/newsletter/ManageSubscription.jsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  unsubscribeNewsletter, 
  getNewsletterStatus 
} from '../../services/newsletterService';
import LoadingSpinner from '../common/LoadingSpinner';
import AlertMessage from '../common/AlertMessage';
import './Newsletter.scss';

const ManageSubscription = () => {
  const [status, setStatus] = useState('idle'); // idle, loading, checking, not-found, confirmed, cancelled, error
  const [message, setMessage] = useState('');
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  
  const { 
    register, 
    handleSubmit, 
    formState: { errors },
    setValue
  } = useForm();
  
  // Controlla se l'email è stata passata tramite query string
  React.useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const email = searchParams.get('email');
    
    if (email) {
      setValue('email', email);
      // Verifica subito lo stato dell'iscrizione
      checkSubscription(email);
    }
  }, [location.search, setValue]);
  
  const checkSubscription = async (email) => {
    try {
      setStatus('checking');
      setMessage('Verifica iscrizione in corso...');
      
      const response = await getNewsletterStatus(email);
      
      if (response.subscribed) {
        setStatus('confirmed');
        setSubscriptionInfo(response);
        setMessage('Email trovata. Sei iscritto alla nostra newsletter.');
      } else {
        setStatus('not-found');
        setMessage('Questa email non risulta iscritta alla newsletter.');
      }
    } catch (error) {
      console.error('Errore durante la verifica:', error);
      setStatus('error');
      setMessage('Si è verificato un errore durante la verifica dell\'iscrizione.');
    }
  };
  
  const onCheckSubmit = async (data) => {
    await checkSubscription(data.email);
  };
  
  const onUnsubscribeSubmit = async () => {
    try {
      setStatus('loading');
      setMessage('Cancellazione in corso...');
      
      const response = await unsubscribeNewsletter(subscriptionInfo.email);
      
      setStatus('cancelled');
      setMessage('Iscrizione cancellata con successo. Non riceverai più le nostre newsletter.');
      setSubscriptionInfo(null);
    } catch (error) {
      console.error('Errore durante la cancellazione:', error);
      setStatus('error');
      setMessage('Si è verificato un errore durante la cancellazione dell\'iscrizione.');
    }
  };
  
  const goToHome = () => {
    navigate('/');
  };
  
  const renderCheckForm = () => (
    <form onSubmit={handleSubmit(onCheckSubmit)} className="manage-form">
      <div className="form-group">
        <label htmlFor="email">Inserisci la tua email per gestire l'iscrizione</label>
        <input
          type="email"
          id="email"
          placeholder="La tua email"
          className={`form-control ${errors.email ? 'is-invalid' : ''}`}
          {...register('email', { 
            required: 'L\'email è obbligatoria', 
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Indirizzo email non valido'
            }
          })}
          disabled={status === 'checking'}
        />
        {errors.email && (
          <div className="invalid-feedback">{errors.email.message}</div>
        )}
      </div>
      
      <button 
        type="submit" 
        className="btn btn-primary" 
        disabled={status === 'checking'}
      >
        {status === 'checking' ? (
          <>
            <LoadingSpinner size="sm" />
            <span className="ms-2">Verifica in corso...</span>
          </>
        ) : (
          'Verifica iscrizione'
        )}
      </button>
    </form>
  );
  
  const renderSubscriptionInfo = () => (
    <div className="subscription-info">
      <div className="subscription-status">
        <h4>Stato iscrizione</h4>
        <p>
          <strong>Email:</strong> {subscriptionInfo.email}
        </p>
        <p>
          <strong>Stato:</strong> {subscriptionInfo.is_active ? 'Attiva' : 'Non attiva'}
        </p>
        <p>
          <strong>Data iscrizione:</strong> {new Date(subscriptionInfo.subscribed_at).toLocaleDateString('it-IT')}
        </p>
      </div>
      
      <div className="manage-actions">
        <button 
          onClick={onUnsubscribeSubmit} 
          className="btn btn-danger"
          disabled={status === 'loading'}
        >
          {status === 'loading' ? (
            <>
              <LoadingSpinner size="sm" />
              <span className="ms-2">Cancellazione...</span>
            </>
          ) : (
            'Cancella iscrizione'
          )}
        </button>
      </div>
    </div>
  );
  
  return (
    <div className="manage-subscription-container">
      <div className="manage-card">
        <h2 className="manage-title">Gestione Iscrizione Newsletter</h2>
        
        {(status === 'idle' || status === 'not-found' || status === 'error') && renderCheckForm()}
        
        {status === 'confirmed' && renderSubscriptionInfo()}
        
        {status === 'cancelled' && (
          <div className="cancellation-success">
            <AlertMessage type="success" message={message} />
            <button onClick={goToHome} className="btn btn-primary mt-3">
              Torna alla home
            </button>
          </div>
        )}
        
        {status === 'not-found' && (
          <AlertMessage type="warning" message={message} />
        )}
        
        {status === 'error' && (
          <AlertMessage type="danger" message={message} />
        )}
      </div>
    </div>
  );
};

export default ManageSubscription;