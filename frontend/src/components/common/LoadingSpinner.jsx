import React from 'react';
import './LoadingSpinner.scss';

const LoadingSpinner = ({ size = 'md' }) => {
  const spinnerClass = `spinner spinner-${size}`;
  
  return (
    <div className={spinnerClass}>
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Caricamento...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;