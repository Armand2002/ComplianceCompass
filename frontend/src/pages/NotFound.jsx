import React from 'react';
import { Link } from 'react-router-dom';
import { FaExclamationTriangle, FaHome } from 'react-icons/fa';

const NotFound = () => {
  return (
    <div className="error-container">
      <FaExclamationTriangle className="error-icon" />
      <h2>Pagina Non Trovata</h2>
      <p>La pagina che stai cercando non esiste o è stata spostata.</p>
      <div className="error-actions">
        <Link to="/" className="button primary">
          <FaHome />
          <span>Torna alla Home</span>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;