// frontend/src/components/common/Modal.jsx
import React, { useEffect, useRef } from 'react';
import { FaTimes } from 'react-icons/fa';
import ReactDOM from 'react-dom';

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  footer, 
  size = 'medium', 
  closeOnOverlayClick = true
}) => {
  const modalRef = useRef(null);
  
  // Gestisci la chiusura con tasto Escape
  useEffect(() => {
    const handleEscapeKey = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscapeKey);
    
    // Blocca lo scroll del body quando la modale è aperta
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);
  
  // Handler per il click sull'overlay
  const handleOverlayClick = (e) => {
    if (modalRef.current && !modalRef.current.contains(e.target) && closeOnOverlayClick) {
      onClose();
    }
  };
  
  // Non renderizzare nulla se la modale non è aperta
  if (!isOpen) return null;
  
  // Calcola la classe di dimensione
  const sizeClass = `modal-${size}`;
  
  return ReactDOM.createPortal(
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className={`modal-container ${sizeClass}`} ref={modalRef}>
        <div className="modal-header">
          <h3 className="modal-title">{title}</h3>
          <button className="modal-close" onClick={onClose}>
            <FaTimes />
          </button>
        </div>
        
        <div className="modal-content">
          {children}
        </div>
        
        {footer && (
          <div className="modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
};

export default Modal;