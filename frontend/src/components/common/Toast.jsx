// frontend/src/components/common/Toast.jsx
import React, { useEffect, useState, createContext, useContext } from 'react';
import ReactDOM from 'react-dom';
import { 
  FaCheck, 
  FaExclamationTriangle, 
  FaInfoCircle, 
  FaExclamationCircle, 
  FaTimes 
} from 'react-icons/fa';

// Tipo di toast
const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Durata predefinita in millisecondi
const DEFAULT_DURATION = 5000;

// Crea context per i toast
const ToastContext = createContext(null);

// Componente per un singolo toast
const ToastItem = ({ id, type, message, onClose, autoClose = true, duration = DEFAULT_DURATION }) => {
  const [visible, setVisible] = useState(true);
  
  // Seleziona icona in base al tipo
  const getIcon = () => {
    switch (type) {
      case TOAST_TYPES.SUCCESS:
        return <FaCheck />;
      case TOAST_TYPES.ERROR:
        return <FaExclamationCircle />;
      case TOAST_TYPES.WARNING:
        return <FaExclamationTriangle />;
      case TOAST_TYPES.INFO:
      default:
        return <FaInfoCircle />;
    }
  };
  
  // Effetto per la chiusura automatica
  useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(() => onClose(id), 300); // Ritardo per l'animazione
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [id, onClose, autoClose, duration]);
  
  // Handler per la chiusura manuale
  const handleClose = () => {
    setVisible(false);
    setTimeout(() => onClose(id), 300); // Ritardo per l'animazione
  };
  
  return (
    <div className={`toast-item ${type} ${visible ? 'visible' : 'hidden'}`}>
      <div className="toast-icon">
        {getIcon()}
      </div>
      <div className="toast-content">
        {message}
      </div>
      <button className="toast-close" onClick={handleClose}>
        <FaTimes />
      </button>
    </div>
  );
};

// Componente container per tutti i toast
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  
  // Aggiunge un nuovo toast
  const showToast = (type, message, options = {}) => {
    const id = Date.now();
    const newToast = {
      id,
      type,
      message,
      ...options
    };
    
    setToasts(prev => [...prev, newToast]);
    return id;
  };
  
  // Rimuove un toast specifico
  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };
  
  // Rimuove tutti i toast
  const clearToasts = () => {
    setToasts([]);
  };
  
  // Helper per mostrare diversi tipi di toast
  const toast = {
    success: (message, options) => showToast(TOAST_TYPES.SUCCESS, message, options),
    error: (message, options) => showToast(TOAST_TYPES.ERROR, message, options),
    warning: (message, options) => showToast(TOAST_TYPES.WARNING, message, options),
    info: (message, options) => showToast(TOAST_TYPES.INFO, message, options),
    remove: removeToast,
    clear: clearToasts
  };
  
  return (
    <ToastContext.Provider value={toast}>
      {children}
      
      {ReactDOM.createPortal(
        <div className="toast-container top-right">
          {toasts.map(toast => (
            <ToastItem
              key={toast.id}
              id={toast.id}
              type={toast.type}
              message={toast.message}
              onClose={removeToast}
              autoClose={toast.autoClose}
              duration={toast.duration}
            />
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
};

// Hook personalizzato per utilizzare i toast
export const useToast = () => {
  const context = useContext(ToastContext);
  
  if (!context) {
    throw new Error('useToast deve essere utilizzato all\'interno di un ToastProvider');
  }
  
  return context;
};

// Esporta anche tipi per l'utilizzo
export { TOAST_TYPES };