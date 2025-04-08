import React from 'react';
import './AlertMessage.scss';

const AlertMessage = ({ type = 'info', message, onClose }) => {
  const alertClass = `alert alert-${type}`;
  
  return (
    <div className={alertClass} role="alert">
      {message}
      {onClose && (
        <button 
          type="button" 
          className="close-button" 
          onClick={onClose}
          aria-label="Chiudi"
        >
          &times;
        </button>
      )}
    </div>
  );
};

export default AlertMessage;