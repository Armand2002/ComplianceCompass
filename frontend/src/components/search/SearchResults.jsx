// frontend/src/components/search/SearchResults.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FaShieldAlt, FaBook, FaCode, FaExclamationTriangle } from 'react-icons/fa';

const SearchResults = ({ results, isLoading, error, searchTerm }) => {
  // Funzione per evidenziare il termine di ricerca nel testo
  const highlightText = (text, term) => {
    if (!term || term.length < 2 || !text) return text;
    
    const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };
  
  // Funzione per determinare l'icona in base al tipo di risultato
  const getResultIcon = (result) => {
    // Determina il tipo di risultato
    if (result.type === 'gdpr') {
      return <FaShieldAlt className="result-icon gdpr" />;
    } else if (result.type === 'pbd') {
      return <FaBook className="result-icon pbd" />;
    } else if (result.type === 'vulnerability') {
      return <FaExclamationTriangle className="result-icon vulnerability" />;
    } else {
      // Default per pattern
      return <FaCode className="result-icon pattern" />;
    }
  };
  
  // Funzione per determinare l'URL del risultato
  const getResultUrl = (result) => {
    // Determina l'URL in base al tipo di risultato
    if (result.type === 'gdpr') {
      return `/gdpr/${result.number}`;
    } else if (result.type === 'pbd') {
      return `/privacy-by-design#${result.id}`;
    } else if (result.type === 'vulnerability') {
      return `/vulnerabilities/${result.id}`;
    } else {
      // Default per pattern
      return `/patterns/${result.id}`;
    }
  };
  
  // Funzione per troncare il testo a una lunghezza massima
  const truncateText = (text, maxLength = 200) => {
    if (!text || text.length <= maxLength) return text;
    
    return text.substring(0, maxLength) + '...';
  };
  
  // Funzione per renderizzare un badge di estratto
  const renderExcerpt = (text, maxLength = 200) => {
    if (!text) return null;
    
    const excerpt = truncateText(text, maxLength);
    const highlighted = searchTerm
      ? <span dangerouslySetInnerHTML={{ __html: highlightText(excerpt, searchTerm) }} />
      : excerpt;
    
    return <p className="result-excerpt">{highlighted}</p>;
  };
  
  // Se sta caricando, mostra indicatore di caricamento
  if (isLoading) {
    return (
      <div className="search-results-loading">
        <div className="loading-spinner"></div>
        <p>Ricerca in corso...</p>
      </div>
    );
  }
  
  // Se c'è un errore, mostra messaggio di errore
  if (error) {
    return (
      <div className="search-results-error">
        <FaExclamationTriangle className="error-icon" />
        <p>{error}</p>
      </div>
    );
  }
  
  // Se non ci sono risultati, mostra messaggio
  if (!results || results.length === 0) {
    return (
      <div className="search-results-empty">
        <p>Nessun risultato trovato. Prova a modificare i termini di ricerca o i filtri.</p>
      </div>
    );
  }
  
  // Altrimenti, mostra i risultati
  return (
    <div className="search-results">
      {results.map(result => (
        <div key={`${result.type || 'pattern'}-${result.id}`} className="search-result-item">
          <div className="result-icon-container">
            {getResultIcon(result)}
          </div>
          
          <div className="result-content">
            <h3 className="result-title">
              <Link to={getResultUrl(result)}>
                {searchTerm 
                  ? <span dangerouslySetInnerHTML={{ __html: highlightText(result.title, searchTerm) }} />
                  : result.title
                }
              </Link>
            </h3>
            
            <div className="result-meta">
              {result.strategy && (
                <span className={`strategy-badge small ${result.strategy.toLowerCase()}`}>
                  {result.strategy}
                </span>
              )}
              
              {result.mvc_component && (
                <span className="mvc-badge small">
                  {result.mvc_component}
                </span>
              )}
              
              {result.number && (
                <span className="meta-item">
                  <FaShieldAlt />
                  <span>Articolo {result.number}</span>
                </span>
              )}
              
              {result.severity && (
                <span className={`severity-badge ${result.severity.toLowerCase()}`}>
                  {result.severity}
                </span>
              )}
            </div>
            
            {renderExcerpt(result.description || result.content)}
            
            {/* Mostra lo score solo se rilevante (es. maggiore di una certa soglia) */}
            {result.score > 1 && (
              <div className="result-score">
                <span>Rilevanza: {Math.round(result.score * 10) / 10}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SearchResults;