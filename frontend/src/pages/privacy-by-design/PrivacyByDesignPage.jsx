// frontend/src/pages/privacy-by-design/PrivacyByDesignPage.jsx
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaBook, FaCode, FaExclamationTriangle } from 'react-icons/fa';
import axios from 'axios';

const PrivacyByDesignPage = () => {
  // Stato per i principi PbD
  const [principles, setPrinciples] = useState([]);
  const [selectedPrinciple, setSelectedPrinciple] = useState(null);
  
  // Stato per i pattern correlati
  const [relatedPatterns, setRelatedPatterns] = useState({});
  
  // Stato per loading e errore
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Ottieni l'hash dall'URL
  const location = useLocation();
  const hash = location.hash.replace('#', '');
  
  // Carica i principi Privacy by Design all'avvio
  useEffect(() => {
    const fetchPrinciples = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await axios.get('/api/pbd/principles');
        setPrinciples(response.data);
        
        // Se c'è un hash nell'URL, seleziona quel principio
        if (hash) {
          const principle = response.data.find(p => p.id.toString() === hash);
          if (principle) {
            setSelectedPrinciple(principle);
          } else {
            // Se non è stato trovato, seleziona il primo
            setSelectedPrinciple(response.data[0]);
          }
        } else if (response.data.length > 0) {
          // Altrimenti seleziona il primo principio
          setSelectedPrinciple(response.data[0]);
        }
      } catch (err) {
        console.error('Errore nel caricamento dei principi PbD:', err);
        setError('Si è verificato un errore nel caricamento dei principi Privacy by Design. Riprova più tardi.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchPrinciples();
  }, [hash]);
  
  // Carica i pattern correlati quando cambia il principio selezionato
  useEffect(() => {
    if (!selectedPrinciple) return;
    
    // Se abbiamo già caricato i pattern per questo principio, non serve ricaricarli
    if (relatedPatterns[selectedPrinciple.id]) return;
    
    const fetchRelatedPatterns = async () => {
      try {
        const response = await axios.get(`/api/patterns/by-pbd/${selectedPrinciple.id}`);
        
        setRelatedPatterns(prev => ({
          ...prev,
          [selectedPrinciple.id]: response.data
        }));
      } catch (err) {
        console.error('Errore nel caricamento dei pattern correlati:', err);
      }
    };
    
    fetchRelatedPatterns();
  }, [selectedPrinciple, relatedPatterns]);
  
  // Gestisce la selezione di un principio
  const handleSelectPrinciple = (principle) => {
    setSelectedPrinciple(principle);
    
    // Aggiorna l'hash nell'URL
    window.history.pushState(null, '', `#${principle.id}`);
  };
  
  // Se sta caricando, mostra indicatore di caricamento
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento principi Privacy by Design in corso...</p>
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
  
  return (
    <div className="pbd-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Privacy by Design</h1>
          <p>Esplora i principi fondamentali di Privacy by Design e i pattern correlati</p>
        </div>
      </div>
      
      <div className="pbd-container">
        <div className="pbd-principles-nav">
          <div className="principles-header">
            <h2>I 7 Principi Fondamentali</h2>
          </div>
          
          <div className="principles-list">
            {principles.map(principle => (
              <div 
                key={principle.id} 
                className={`principle-item ${selectedPrinciple?.id === principle.id ? 'active' : ''}`}
                onClick={() => handleSelectPrinciple(principle)}
              >
                <FaBook className="principle-icon" />
                <div className="principle-info">
                  <h3 className="principle-name">{principle.name}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="pbd-content">
          {selectedPrinciple ? (
            <div className="principle-detail">
              <div className="principle-header">
                <h2>{selectedPrinciple.name}</h2>
              </div>
              
              <div className="principle-body">
                <p className="principle-description">{selectedPrinciple.description}</p>
                
                {selectedPrinciple.guidance && (
                  <div className="principle-guidance">
                    <h3>Linee guida</h3>
                    <p>{selectedPrinciple.guidance}</p>
                  </div>
                )}
              </div>
              
              {/* Pattern correlati */}
              <div className="principle-patterns">
                <h3>Pattern che implementano questo principio</h3>
                
                {relatedPatterns[selectedPrinciple.id] ? (
                  relatedPatterns[selectedPrinciple.id].length > 0 ? (
                    <div className="related-patterns-grid">
                      {relatedPatterns[selectedPrinciple.id].map(pattern => (
                        <div key={pattern.id} className="pbd-pattern-card">
                          <div className="pbd-pattern-header">
                            <span className={`strategy-badge ${pattern.strategy.toLowerCase()}`}>
                              {pattern.strategy}
                            </span>
                            <h4 className="pbd-pattern-title">
                              <Link to={`/patterns/${pattern.id}`}>{pattern.title}</Link>
                            </h4>
                          </div>
                          
                          <p className="pbd-pattern-description">
                            {pattern.description.length > 150 
                              ? `${pattern.description.substring(0, 150)}...` 
                              : pattern.description
                            }
                          </p>
                          
                          <div className="pbd-pattern-footer">
                            <span className="mvc-component">
                              <FaCode />
                              <span>{pattern.mvc_component}</span>
                            </span>
                            
                            <Link to={`/patterns/${pattern.id}`} className="view-pattern">
                              Vedi Pattern
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-patterns">
                      <p>Nessun pattern trovato per questo principio.</p>
                    </div>
                  )
                ) : (
                  <div className="loading-patterns">
                    <div className="loading-spinner small"></div>
                    <p>Caricamento pattern correlati...</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="principle-placeholder">
              <FaBook className="placeholder-icon" />
              <h2>Seleziona un principio</h2>
              <p>Seleziona un principio dalla lista per visualizzarne i dettagli</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PrivacyByDesignPage;