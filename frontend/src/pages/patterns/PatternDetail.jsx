import React, { useContext, useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  FaEdit, 
  FaTrash, 
  FaShieldAlt, 
  FaCode, 
  FaLock, 
  FaRegClock,
  FaChevronLeft,
  FaExclamationTriangle,
  FaUserAlt
} from 'react-icons/fa';
import { format } from 'date-fns';
import { it } from 'date-fns/locale';

import { PatternContext } from '../../context/PatternContext';
import { AuthContext } from '../../context/AuthContext';
import RelatedPatterns from '../../components/patterns/RelatedPatterns';

const PatternDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const { currentPattern, loadPattern, deletePattern, isLoading, error } = useContext(PatternContext);
  const { user } = useContext(AuthContext);
  
  // Stato per la modale di conferma eliminazione
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  // Stato per i pattern correlati
  const [relatedPatterns, setRelatedPatterns] = useState([]);
  // Stato per tenere traccia del caricamento dei pattern correlati
  const [loadingRelated, setLoadingRelated] = useState(false);
  
  // Carica i dettagli del pattern quando cambia l'ID
  useEffect(() => {
    const fetchPattern = async () => {
      await loadPattern(id);
    };
    
    fetchPattern();
  }, [id, loadPattern]);
  
  // Carica i pattern correlati quando viene caricato il pattern corrente
  useEffect(() => {
    if (currentPattern) {
      const fetchRelatedPatterns = async () => {
        setLoadingRelated(true);
        try {
          const related = await PatternContext.getRelatedPatterns(currentPattern.id, 5);
          setRelatedPatterns(related);
        } catch (err) {
          console.error('Errore nel caricamento dei pattern correlati:', err);
        } finally {
          setLoadingRelated(false);
        }
      };
      
      fetchRelatedPatterns();
    }
  }, [currentPattern]);
  
  // Verifica se l'utente può modificare o eliminare il pattern
  const canEditPattern = user?.role === 'admin' || (user?.role === 'editor' && currentPattern?.created_by_id === user.id);
  
  // Gestisce l'eliminazione del pattern
  const handleDeletePattern = async () => {
    try {
      await deletePattern(id);
      navigate('/patterns');
    } catch (err) {
      console.error('Errore nell\'eliminazione del pattern:', err);
    }
  };
  
  // Formatta la data
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'dd MMMM yyyy, HH:mm', { locale: it });
    } catch (error) {
      return dateString;
    }
  };
  
  // Se il pattern è in caricamento, mostra un loader
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento pattern...</p>
      </div>
    );
  }
  
  // Se si è verificato un errore, mostra un messaggio di errore
  if (error) {
    return (
      <div className="error-container">
        <FaExclamationTriangle className="error-icon" />
        <h2>Si è verificato un errore</h2>
        <p>{error}</p>
        <div className="error-actions">
          <button className="button secondary" onClick={() => navigate('/patterns')}>
            <FaChevronLeft />
            <span>Torna ai Pattern</span>
          </button>
          <button className="button primary" onClick={() => loadPattern(id)}>
            Riprova
          </button>
        </div>
      </div>
    );
  }
  
  // Se il pattern non è stato trovato, mostra un messaggio
  if (!currentPattern) {
    return (
      <div className="not-found-container">
        <h2>Pattern non trovato</h2>
        <p>Il pattern richiesto non esiste o è stato rimosso.</p>
        <Link to="/patterns" className="button primary">
          <FaChevronLeft />
          <span>Torna ai Pattern</span>
        </Link>
      </div>
    );
  }
  
  return (
    <div className="pattern-detail-page">
      {/* Header con navigazione e azioni */}
      <div className="page-header">
        <div className="breadcrumb">
          <Link to="/patterns" className="breadcrumb-link">
            <FaChevronLeft />
            <span>Tutti i Pattern</span>
          </Link>
        </div>
        
        {canEditPattern && (
          <div className="header-actions">
            <Link to={`/patterns/${id}/edit`} className="button secondary">
              <FaEdit />
              <span>Modifica</span>
            </Link>
            <button className="button danger" onClick={() => setShowDeleteModal(true)}>
              <FaTrash />
              <span>Elimina</span>
            </button>
          </div>
        )}
      </div>
      
      {/* Intestazione Pattern */}
      <div className="pattern-header">
        <div className="pattern-header-content">
          <div className="pattern-badges">
            <span className={`strategy-badge ${currentPattern.strategy.toLowerCase()}`}>
              {currentPattern.strategy}
            </span>
            <span className="mvc-badge">
              {currentPattern.mvc_component}
            </span>
          </div>
          
          <h1 className="pattern-title">{currentPattern.title}</h1>
          
          <div className="pattern-meta">
            <div className="meta-item">
              <FaRegClock />
              <span>Aggiornato: {formatDate(currentPattern.updated_at)}</span>
            </div>
            
            {currentPattern.created_by && (
              <div className="meta-item">
                <FaUserAlt />
                <span>Creato da: {currentPattern.created_by.username}</span>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Contenuto principale */}
      <div className="pattern-content">
        <div className="pattern-main">
          <section className="pattern-section">
            <h2>Descrizione</h2>
            <div className="section-content">
              <p>{currentPattern.description}</p>
            </div>
          </section>
          
          <section className="pattern-section">
            <h2>Contesto</h2>
            <div className="section-content">
              <p>{currentPattern.context}</p>
            </div>
          </section>
          
          <section className="pattern-section">
            <h2>Problema</h2>
            <div className="section-content">
              <p>{currentPattern.problem}</p>
            </div>
          </section>
          
          <section className="pattern-section">
            <h2>Soluzione</h2>
            <div className="section-content">
              <p>{currentPattern.solution}</p>
            </div>
          </section>
          
          <section className="pattern-section">
            <h2>Conseguenze</h2>
            <div className="section-content">
              <p>{currentPattern.consequences}</p>
            </div>
          </section>
          
          {currentPattern.examples && currentPattern.examples.length > 0 && (
            <section className="pattern-section">
              <h2>Esempi di Implementazione</h2>
              <div className="section-content">
                {currentPattern.examples.map(example => (
                  <div key={example.id} className="example-container">
                    <h3>{example.title}</h3>
                    <p>{example.description}</p>
                    {example.language && example.code && (
                      <div className="code-block">
                        <div className="code-header">
                          <span>{example.language}</span>
                        </div>
                        <pre>
                          <code>{example.code}</code>
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
        
        <div className="pattern-sidebar">
          <div className="sidebar-section">
            <h3>Informazioni</h3>
            <div className="info-item">
              <strong>Strategia:</strong>
              <span>{currentPattern.strategy}</span>
            </div>
            <div className="info-item">
              <strong>Componente MVC:</strong>
              <span>{currentPattern.mvc_component}</span>
            </div>
          </div>
          
          {currentPattern.gdpr_articles && currentPattern.gdpr_articles.length > 0 && (
            <div className="sidebar-section">
              <h3>Articoli GDPR</h3>
              <ul className="gdpr-list">
                {currentPattern.gdpr_articles.map(article => (
                  <li key={article.id}>
                    <Link to={`/gdpr/${article.number}`} className="gdpr-link">
                      <FaShieldAlt />
                      <span>Art. {article.number} - {article.title}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {currentPattern.pbd_principles && currentPattern.pbd_principles.length > 0 && (
            <div className="sidebar-section">
              <h3>Principi Privacy by Design</h3>
              <ul className="pbd-list">
                {currentPattern.pbd_principles.map(principle => (
                  <li key={principle.id}>
                    <span className="pbd-item">
                      <FaLock />
                      <span>{principle.name}</span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {currentPattern.iso_phases && currentPattern.iso_phases.length > 0 && (
            <div className="sidebar-section">
              <h3>Fasi ISO</h3>
              <ul className="iso-list">
                {currentPattern.iso_phases.map(phase => (
                  <li key={phase.id}>
                    <span className="iso-item">
                      <FaCode />
                      <span>{phase.name}</span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {currentPattern.vulnerabilities && currentPattern.vulnerabilities.length > 0 && (
            <div className="sidebar-section">
              <h3>Vulnerabilità</h3>
              <ul className="vulnerability-list">
                {currentPattern.vulnerabilities.map(vuln => (
                  <li key={vuln.id}>
                    <span className={`vulnerability-item ${vuln.severity.toLowerCase()}`}>
                      <FaExclamationTriangle />
                      <span>{vuln.name}</span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Pattern correlati */}
          <div className="sidebar-section">
            <h3>Pattern Correlati</h3>
            {loadingRelated ? (
              <div className="loading-container small">
                <div className="loading-spinner"></div>
                <p>Caricamento...</p>
              </div>
            ) : relatedPatterns.length > 0 ? (
              <RelatedPatterns patterns={relatedPatterns} />
            ) : (
              <p className="no-related">Nessun pattern correlato trovato.</p>
            )}
          </div>
        </div>
      </div>
      
      {/* Modale di conferma eliminazione */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <h3>Conferma eliminazione</h3>
            </div>
            <div className="modal-content">
              <p>Sei sicuro di voler eliminare il pattern <strong>{currentPattern.title}</strong>?</p>
              <p className="warning-text">Questa azione non può essere annullata.</p>
            </div>
            <div className="modal-footer">
              <button 
                className="button secondary" 
                onClick={() => setShowDeleteModal(false)}
              >
                Annulla
              </button>
              <button 
                className="button danger" 
                onClick={handleDeletePattern}
              >
                Elimina
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatternDetail;