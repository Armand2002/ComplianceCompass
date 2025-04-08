// frontend/src/components/newsletter/NewsletterSubscription.jsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { subscribeNewsletter } from '../../services/newsletterService';
import LoadingSpinner from '../common/LoadingSpinner';
import AlertMessage from '../common/AlertMessage';
import './Newsletter.scss';

const NewsletterSubscription = () => {
  const [status, setStatus] = useState('idle'); // idle, loading, success, error, already-subscribed
  const [message, setMessage] = useState('');
  const { 
    register, 
    handleSubmit, 
    reset, 
    formState: { errors } 
  } = useForm();
  
  const onSubmit = async (data) => {
    try {
      setStatus('loading');
      setMessage('');
      
      const response = await subscribeNewsletter(data.email);
      
      if (response.already_subscribed) {
        setStatus('already-subscribed');
        setMessage('Questa email è già iscritta alla newsletter.');
      } else if (response.requires_verification) {
        setStatus('success');
        setMessage('Ti abbiamo inviato una email di verifica. Per completare l\'iscrizione, segui le istruzioni contenute nel messaggio.');
        reset(); // Reset form
      } else {
        setStatus('success');
        setMessage('Iscrizione completata con successo!');
        reset(); // Reset form
      }
    } catch (error) {
      console.error('Errore durante l\'iscrizione:', error);
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Si è verificato un errore durante l\'iscrizione. Riprova più tardi.');
    }
  };
  
  return (
    <div className="newsletter-container">
      <h3 className="newsletter-title">Resta aggiornato sui Privacy Pattern</h3>
      <p className="newsletter-description">
        Iscriviti alla newsletter per ricevere aggiornamenti sui nuovi privacy pattern, 
        modifiche normative e casi studio di Privacy by Design.
      </p>
      
      {status === 'success' || status === 'already-subscribed' ? (
        <AlertMessage 
          type={status === 'success' ? 'success' : 'info'} 
          message={message} 
        />
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="newsletter-form">
          <div className="form-group">
            <input
              type="email"
              placeholder="Inserisci la tua email"
              className={`form-control ${errors.email ? 'is-invalid' : ''}`}
              {...register('email', { 
                required: 'L\'email è obbligatoria', 
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Indirizzo email non valido'
                }
              })}
              disabled={status === 'loading'}
            />
            {errors.email && (
              <div className="invalid-feedback">{errors.email.message}</div>
            )}
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary newsletter-submit" 
            disabled={status === 'loading'}
          >
            {status === 'loading' ? (
              <>
                <LoadingSpinner size="sm" />
                <span className="ms-2">Iscrizione in corso...</span>
              </>
            ) : (
              'Iscriviti alla newsletter'
            )}
          </button>
          
          {status === 'error' && (
            <AlertMessage type="danger" message={message} />
          )}
          
          <p className="newsletter-privacy-note">
            Iscrivendoti, accetti di ricevere email in conformità con la nostra 
            <a href="/privacy-policy" className="ms-1">Privacy Policy</a>.
            Potrai annullare l'iscrizione in qualsiasi momento.
          </p>
        </form>
      )}
    </div>
  );
};

export default NewsletterSubscription;