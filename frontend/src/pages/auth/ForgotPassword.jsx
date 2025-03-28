import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { FaEnvelope, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import AuthService from '../../api/authService';

// Schema di validazione
const ForgotPasswordSchema = Yup.object().shape({
  email: Yup.string()
    .email('Email non valida')
    .required('Email obbligatoria'),
});

const ForgotPassword = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    setFormError('');
    setIsSubmitting(true);
    
    try {
      await AuthService.requestPasswordReset(values.email);
      setSuccess(true);
      resetForm();
    } catch (err) {
      setFormError('Si è verificato un errore. Riprova più tardi.');
      console.error('Errore nella richiesta di reset password:', err);
    } finally {
      setSubmitting(false);
      setIsSubmitting(false);
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
            <h2>Password Dimenticata</h2>
            <p>Inserisci la tua email per ricevere un link di reset</p>
          </div>
          
          {formError && (
            <div className="auth-error">
              <FaExclamationTriangle />
              <span>{formError}</span>
            </div>
          )}
          
          {success ? (
            <div className="auth-success">
              <FaCheckCircle />
              <h3>Email Inviata!</h3>
              <p>Se l'indirizzo email esiste nel nostro sistema, riceverai un link per reimpostare la tua password.</p>
              <Link to="/login" className="button primary">
                Torna al Login
              </Link>
            </div>
          ) : (
            <Formik
              initialValues={{ email: '' }}
              validationSchema={ForgotPasswordSchema}
              onSubmit={handleSubmit}
            >
              {({ touched, errors }) => (
                <Form className="auth-form">
                  <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <div className={`input-with-icon ${touched.email && errors.email ? 'has-error' : ''}`}>
                      <FaEnvelope className="input-icon" />
                      <Field type="email" id="email" name="email" placeholder="La tua email" />
                    </div>
                    <ErrorMessage name="email" component="div" className="error-message" />
                  </div>
                  
                  <button 
                    type="submit" 
                    className="auth-button" 
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Invio in corso...' : 'Invia Link di Reset'}
                  </button>
                </Form>
              )}
            </Formik>
          )}
          
          <div className="auth-footer">
            <p>Ricordi la password? <Link to="/login">Accedi</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;