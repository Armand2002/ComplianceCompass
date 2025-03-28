// frontend/src/pages/patterns/PatternEdit.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FaChevronLeft, FaExclamationTriangle } from 'react-icons/fa';
import { PatternContext } from '../../context/PatternContext';
import PatternForm from '../../components/patterns/PatternForm';
import axios from 'axios';

const PatternEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loadPattern, updatePattern } = useContext(PatternContext);
  
  // Stato per il pattern e dati relazionati
  const [pattern, setPattern] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gdprArticles, setGdprArticles] = useState([]);
  const [pbdPrinciples, setPbdPrinciples] = useState([]);
  const [isoPhases, setIsoPhases] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  
  // Carica il pattern e i dati di relazione all'avvio
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Carica pattern
        const patternData = await loadPattern(id);
        setPattern(patternData);
        
        // Carica articoli GDPR
        const gdprResponse = await axios.get('/api/gdpr/articles');
        setGdprArticles(gdprResponse.data);
        
        // Carica principi PbD
        const pbdResponse = await axios.get('/api/pbd/principles');
        setPbdPrinciples(pbdResponse.data);
        
        // Carica fasi ISO
        const isoResponse = await axios.get('/api/iso/phases');
        setIsoPhases(isoResponse.data);
        
        // Carica vulnerabilità
        const vulnResponse = await axios.get('/api/vulnerabilities');
        setVulnerabilities(vulnResponse.data);
      } catch (err) {
        console.error('Errore nel caricamento dei dati:', err);
        setError('Si è verificato un errore nel caricamento dei dati. Riprova più tardi.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [id, loadPattern]);
  
  // Prepara i valori iniziali per il form
  const prepareInitialValues = () => {
    if (!pattern) return {};
    
    // Estrai gli ID degli articoli GDPR
    const gdpr_ids = pattern.gdpr_articles
      ? pattern.gdpr_articles.map(article => article.id.toString())
      : [];
    
    // Estrai gli ID dei principi PbD
    const pbd_ids = pattern.pbd_principles
      ? pattern.pbd_principles.map(principle => principle.id.toString())
      : [];
    
    // Estrai gli ID delle fasi ISO
    const iso_ids = pattern.iso_phases
      ? pattern.iso_phases.map(phase => phase.id.toString())
      : [];
    
    // Estrai gli ID delle vulnerabilità
    const vulnerability_ids = pattern.vulnerabilities
      ? pattern.vulnerabilities.map(vuln => vuln.id.toString())
      : [];
    
    return {
      ...pattern,
      gdpr_ids,
      pbd_ids,
      iso_ids,
      vulnerability_ids
    };
  };
  
  // Gestore per il submit del form
  const handleSubmit = async (patternData) => {
    try {
      const result = await updatePattern(id, patternData);
      
      if (result) {
        // Reindirizza alla pagina di dettaglio del pattern aggiornato
        navigate(`/patterns/${result.id}`);
      }
    } catch (err) {
      console.error('Errore nell\'aggiornamento del pattern:', err);
      throw new Error(err.response?.data?.detail || 'Errore nell\'aggiornamento del pattern');
    }
  };
  
  // Gestore per l'annullamento
  const handleCancel = () => {
    navigate(`/patterns/${id}`);
  };
  
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento pattern in corso...</p>
      </div>
    );
  }
  
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
  
  if (!pattern) {
    return (
      <div className="not-found-container">
        <h2>Pattern non trovato</h2>
        <p>Il pattern richiesto non esiste o è stato rimosso.</p>
        <button className="button primary" onClick={() => navigate('/patterns')}>
          <FaChevronLeft />
          <span>Torna ai Pattern</span>
        </button>
      </div>
    );
  }
  
  return (
    <div className="pattern-edit-page">
      <div className="page-header">
        <div className="breadcrumb">
          <button className="breadcrumb-link" onClick={() => navigate(`/patterns/${id}`)}>
            <FaChevronLeft />
            <span>Torna al Pattern</span>
          </button>
        </div>
        
        <div className="header-content">
          <h1>Modifica Pattern</h1>
          <p>Modifica i dettagli del pattern: {pattern.title}</p>
        </div>
      </div>
      
      <div className="pattern-form-wrapper">
        <PatternForm 
          initialValues={prepareInitialValues()}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isEdit={true}
          gdprArticles={gdprArticles}
          pbdPrinciples={pbdPrinciples}
          isoPhases={isoPhases}
          vulnerabilities={vulnerabilities}
        />
      </div>
    </div>
  );
};

export default PatternEdit;