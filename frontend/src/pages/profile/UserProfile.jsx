// frontend/src/pages/profile/UserProfile.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { 
  FaUser, 
  FaLock, 
  FaExclamationTriangle, 
  FaSave, 
  FaList, 
  FaEnvelope, 
  FaRegClock 
} from 'react-icons/fa';

import { AuthContext } from '../../context/AuthContext';
import FormField from '../../components/common/FormField';
import Modal from '../../components/common/Modal';
import axios from 'axios';

// Schema di validazione per il form del profilo
const ProfileSchema = Yup.object().shape({
  username: Yup.string()
    .min(3, 'L\'username deve essere di almeno 3 caratteri')
    .max(50, 'L\'username non può superare i 50 caratteri')
    .required('L\'username è obbligatorio'),
  email: Yup.string()
    .email('Email non valida')
    .required('Email obbligatoria'),
  full_name: Yup.string()
    .max(100, 'Il nome completo non può superare i 100 caratteri'),
  bio: Yup.string()
    .max(500, 'La biografia non può superare i 500 caratteri')
});

// Schema di validazione per il cambio password
const PasswordSchema = Yup.object().shape({
  current_password: Yup.string()
    .min(8, 'La password deve essere di almeno 8 caratteri')
    .required('Password attuale obbligatoria'),
  new_password: Yup.string()
    .min(8, 'La nuova password deve essere di almeno 8 caratteri')
    .required('Nuova password obbligatoria'),
  confirm_password: Yup.string()
    .oneOf([Yup.ref('new_password'), null], 'Le password non corrispondono')
    .required('Conferma password obbligatoria')
});

const UserProfile = () => {
  const { user, updateUserData } = useContext(AuthContext);
  const navigate = useNavigate();
  
  // Stato per il profilo utente completo
  const [profile, setProfile] = useState(null);
  const [userPatterns, setUserPatterns] = useState([]);
  
  // Stato per modali
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  
  // Stato per loading e errori
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [passwordChangeError, setPasswordChangeError] = useState(null);
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState(false);
  
  // Carica il profilo utente completo all'avvio
  useEffect(() => {
    const fetchUserProfile = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Carica profilo utente
        const profileResponse = await axios.get('/api/users/profile');
        setProfile(profileResponse.data);
        
        // Carica pattern creati dall'utente
        const patternsResponse = await axios.get('/api/patterns/by-user');
        setUserPatterns(patternsResponse.data);
      } catch (err) {
        console.error('Errore nel caricamento del profilo utente:', err);
        setError('Si è verificato un errore nel caricamento del profilo. Riprova più tardi.');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (user) {
      fetchUserProfile();
    } else {
      navigate('/login');
    }
  }, [user, navigate]);
  
  // Handler per submit del form profilo
  const handleProfileSubmit = async (values, { setSubmitting }) => {
    try {
      const response = await axios.put('/api/users/me', values);
      
      // Aggiorna lo stato locale
      setProfile(response.data);
      
      // Aggiorna il contesto di autenticazione
      updateUserData();
    } catch (err) {
      console.error('Errore nell\'aggiornamento del profilo:', err);
      setError('Si è verificato un errore nell\'aggiornamento del profilo. Riprova più tardi.');
    } finally {
      setSubmitting(false);
    }
  };
  
  // Handler per submit del form cambio password
  const handlePasswordSubmit = async (values, { setSubmitting, resetForm }) => {
    setPasswordChangeError(null);
    setPasswordChangeSuccess(false);
    
    try {
      await axios.post('/api/auth/change-password', {
        current_password: values.current_password,
        new_password: values.new_password,
        confirm_password: values.confirm_password
      });
      
      // Resetta il form e mostra messaggio di successo
      resetForm();
      setPasswordChangeSuccess(true);
      
      // Chiudi la modale dopo un po'
      setTimeout(() => {
        setShowPasswordModal(false);
        setPasswordChangeSuccess(false);
      }, 2000);
    } catch (err) {
      console.error('Errore nel cambio password:', err);
      setPasswordChangeError(err.response?.data?.detail || 'Si è verificato un errore durante il cambio password. Riprova più tardi.');
    } finally {
      setSubmitting(false);
    }
  };
  
  // Se sta caricando, mostra indicatore di caricamento
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento profilo in corso...</p>
      </div>
    );
  }
  
  // Se c'è un errore, mostra messaggio di errore
  if (error) {
    return (
      <div className="error-container">
        <FaExclamationTriangle className="error-icon" />
        <h2>Si è verificato un errore</h2>
        <p>{error}</p>
        <button className="button primary" onClick={() => window.location.reload()}>
          Riprova
        </button>
      </div>
    );
  }
  
  // Se non c'è un profilo, mostra messaggio
  if (!profile) {
    return (
      <div className="error-container">
        <FaUser className="error-icon" />
        <h2>Profilo non disponibile</h2>
        <p>Non è stato possibile caricare il tuo profilo. Prova ad accedere nuovamente.</p>
        <button className="button primary" onClick={() => navigate('/login')}>
          Accedi
        </button>
      </div>
    );
  }
  
  return (
    <div className="profile-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Profilo Utente</h1>
          <p>Gestisci i tuoi dati personali e le preferenze</p>
        </div>
      </div>
      
      <div className="profile-container">
        <div className="profile-sidebar">
          <div className="user-info">
            <div className="user-avatar">
              {profile.avatar_url ? (
                <img src={profile.avatar_url} alt={profile.username} />
              ) : (
                <FaUser className="avatar-placeholder" />
              )}
            </div>
            
            <h2>{profile.username}</h2>
            <p className="user-role">{profile.role}</p>
            
            <div className="user-meta">
              <div className="meta-item">
                <FaEnvelope />
                <span>{profile.email}</span>
              </div>
              {profile.last_login && (
                <div className="meta-item">
                  <FaRegClock />
                  <span>Ultimo accesso: {new Date(profile.last_login).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="sidebar-actions">
            <button 
              className="button secondary password-button"
              onClick={() => setShowPasswordModal(true)}
            >
              <FaLock />
              <span>Cambia Password</span>
            </button>
          </div>
          
          {/* Statistiche utente */}
          <div className="user-stats">
            <h3>Le tue statistiche</h3>
            
            <div className="stat-item">
              <FaList className="stat-icon" />
              <div className="stat-content">
                <span className="stat-label">Pattern Creati</span>
                <span className="stat-value">{profile.created_patterns_count || 0}</span>
              </div>
            </div>
            
            {/* Altre statistiche utente... */}
          </div>
        </div>
        
        <div className="profile-content">
          <div className="profile-section">
            <h2>Informazioni Personali</h2>
            
            <Formik
              initialValues={{
                username: profile.username || '',
                email: profile.email || '',
                full_name: profile.full_name || '',
                bio: profile.bio || ''
              }}
              validationSchema={ProfileSchema}
              onSubmit={handleProfileSubmit}
            >
              {({ isSubmitting, touched, errors }) => (
                <Form className="profile-form">
                  <FormField 
                    name="username"
                    label="Username"
                    type="text"
                    placeholder="Il tuo username"
                    touched={touched}
                    errors={errors}
                    required
                  />
                  
                  <FormField 
                    name="email"
                    label="Email"
                    type="email"
                    placeholder="La tua email"
                    touched={touched}
                    errors={errors}
                    required
                  />
                  
                  <FormField 
                    name="full_name"
                    label="Nome Completo"
                    type="text"
                    placeholder="Il tuo nome completo"
                    touched={touched}
                    errors={errors}
                  />
                  
                  <FormField 
                    name="bio"
                    label="Biografia"
                    type="textarea"
                    placeholder="Racconta qualcosa su di te"
                    touched={touched}
                    errors={errors}
                    fieldProps={{ rows: 4 }}
                  />
                  
                  <div className="form-actions">
                    <button 
                      type="submit" 
                      className="button primary" 
                      disabled={isSubmitting}
                    >
                      <FaSave />
                      <span>{isSubmitting ? 'Salvataggio...' : 'Salva Modifiche'}</span>
                    </button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
          
          {/* Pattern creati dall'utente */}
          <div className="profile-section">
            <h2>I tuoi Pattern</h2>
            
            {userPatterns.length > 0 ? (
              <div className="user-patterns">
                <ul className="user-patterns-list">
                  {userPatterns.map(pattern => (
                    <li key={pattern.id} className="user-pattern-item">
                      <div className="pattern-info">
                        <h3 className="pattern-title">
                          <a href={`/patterns/${pattern.id}`}>{pattern.title}</a>
                        </h3>
                        <div className="pattern-meta">
                          <span className={`strategy-badge small ${pattern.strategy.toLowerCase()}`}>
                            {pattern.strategy}
                          </span>
                          <span className="mvc-badge small">
                            {pattern.mvc_component}
                          </span>
                          <span className="date">
                            <FaRegClock />
                            <span>{new Date(pattern.updated_at).toLocaleDateString()}</span>
                          </span>
                        </div>
                      </div>
                      <div className="pattern-actions">
                        <a href={`/patterns/${pattern.id}`} className="button secondary small">
                          Visualizza
                        </a>
                        <a href={`/patterns/${pattern.id}/edit`} className="button primary small">
                          Modifica
                        </a>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="no-patterns">
                <p>Non hai ancora creato nessun pattern.</p>
                <a href="/patterns/create" className="button primary">
                  Crea il tuo primo pattern
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Modale per il cambio password */}
      <Modal
        isOpen={showPasswordModal}
        onClose={() => {
          setShowPasswordModal(false);
          setPasswordChangeError(null);
          setPasswordChangeSuccess(false);
        }}
        title="Cambia Password"
      >
        <Formik
          initialValues={{
            current_password: '',
            new_password: '',
            confirm_password: ''
          }}
          validationSchema={PasswordSchema}
          onSubmit={handlePasswordSubmit}
        >
          {({ isSubmitting, touched, errors }) => (
            <Form className="password-form">
              {passwordChangeError && (
                <div className="form-error">
                  <FaExclamationTriangle />
                  <span>{passwordChangeError}</span>
                </div>
              )}
              
              {passwordChangeSuccess && (
                <div className="form-success">
                  <span>Password cambiata con successo!</span>
                </div>
              )}
              
              <FormField 
                name="current_password"
                label="Password Attuale"
                type="password"
                placeholder="Inserisci la tua password attuale"
                touched={touched}
                errors={errors}
                required
              />
              
              <FormField 
                name="new_password"
                label="Nuova Password"
                type="password"
                placeholder="Inserisci la nuova password"
                touched={touched}
                errors={errors}
                required
              />
              
              <FormField 
                name="confirm_password"
                label="Conferma Password"
                type="password"
                placeholder="Conferma la nuova password"
                touched={touched}
                errors={errors}
                required
              />
              
              <div className="form-actions">
                <button 
                  type="button" 
                  className="button secondary" 
                  onClick={() => setShowPasswordModal(false)}
                  disabled={isSubmitting}
                >
                  Annulla
                </button>
                <button 
                  type="submit" 
                  className="button primary" 
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Aggiornamento...' : 'Aggiorna Password'}
                </button>
              </div>
            </Form>
          )}
        </Formik>
      </Modal>
    </div>
  );
};

export default UserProfile;