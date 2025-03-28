// frontend/src/pages/patterns/PatternCreate.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaChevronLeft, FaExclamationTriangle } from 'react-icons/fa';
import { PatternContext } from '../../context/PatternContext';
import PatternForm from '../../components/patterns/PatternForm';
import axios from 'axios';

const PatternCreate = () => {
  const navigate = useNavigate();
  const { createPattern } = useContext(PatternContext);
  
  // Stato per errori e dati di relazione
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [gdprArticles, setGdprArticles] = useState([]);
  const [pbdPrinciples, setPbdPrinciples] = useState([]);
  const [isoPhases, setIsoPhases] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  
  // Carica dati di relazione all'avvio
  useEffect(() => {
    const fetchRelationData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
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
        console.error('Errore nel caricamento dei dati di relazione:', err);
        setError('Si è verificato un errore nel caricamento dei dati. Riprova più tardi.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchRelationData();
  }, []);
  
  // Gestore per il submit del form
  const handleSubmit = async (patternData) => {
    try {
      const result = await createPattern(patternData);
      
      if (result) {
        // Reindirizza alla pagina di dettaglio del pattern creato
        navigate(`/patterns/${result.id}`);
      }
    } catch (err) {
      console.error('Errore nella creazione del pattern:', err);
      throw new Error(err.response?.data?.detail || 'Errore nella creazione del pattern');
    }
  };
  
  // Gestore per l'annullamento
  const handleCancel = () => {
    navigate('/patterns');
  };
  
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento dati in corso...</p>
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
  
  return (
    <div className="pattern-create-page">
      <div className="page-header">
        <div className="breadcrumb">
          <button className="breadcrumb-link" onClick={() => navigate('/patterns')}>
            <FaChevronLeft />
            <span>Tutti i Pattern</span>
          </button>
        </div>
        
        <div className="header-content">
          <h1>Crea Nuovo Pattern</h1>
          <p>Compila il form per creare un nuovo Privacy Pattern</p>
        </div>
      </div>
      
      <div className="pattern-form-wrapper">
        <PatternForm 
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          gdprArticles={gdprArticles}
          pbdPrinciples={pbdPrinciples}
          isoPhases={isoPhases}
          vulnerabilities={vulnerabilities}
        />
      </div>
    </div>
  );
};

export default PatternCreate;