import React, { createContext, useState, useEffect, useCallback } from 'react';
import PatternService from '../api/patternService';

// Creazione del contesto
export const PatternContext = createContext();

/**
 * Provider per il contesto dei Privacy Patterns
 * @param {Object} props - Props del componente
 */
export const PatternProvider = ({ children }) => {
  const [patterns, setPatterns] = useState([]);
  const [currentPattern, setCurrentPattern] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalPatterns, setTotalPatterns] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState({
    strategy: null,
    mvc_component: null,
    gdpr_id: null,
    pbd_id: null,
    iso_id: null,
    vulnerability_id: null,
    search: null,
  });

  /**
   * Carica la lista dei pattern con paginazione e filtri
   * @param {number} page - Pagina corrente
   * @param {number} limit - Numero di elementi per pagina
   * @param {Object} filterOptions - Opzioni di filtro
   */
  const loadPatterns = useCallback(async (page = 1, limit = 10, filterOptions = {}) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Combina i filtri esistenti con quelli forniti
      const combinedFilters = { ...filters, ...filterOptions };
      
      // Ottieni i pattern dal servizio
      const response = await PatternService.getPatterns({
        page,
        limit,
        ...combinedFilters,
      });
      
      // Aggiorna lo stato
      setPatterns(response.patterns);
      setTotalPatterns(response.total);
      setCurrentPage(response.page);
      setTotalPages(response.pages);
      setPageSize(response.size);
      
      // Aggiorna i filtri solo se sono stati forniti nuovi filtri
      if (Object.keys(filterOptions).length > 0) {
        setFilters(combinedFilters);
      }
      
      return response;
    } catch (err) {
      console.error('Errore nel caricamento dei pattern:', err);
      setError(err.response?.data?.detail || 'Errore nel caricamento dei pattern');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  /**
   * Carica un pattern specifico per ID
   * @param {number} id - ID del pattern
   */
  const loadPattern = useCallback(async (id) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const pattern = await PatternService.getPattern(id);
      setCurrentPattern(pattern);
      return pattern;
    } catch (err) {
      console.error(`Errore nel caricamento del pattern ${id}:`, err);
      setError(err.response?.data?.detail || 'Errore nel caricamento del pattern');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Crea un nuovo pattern
   * @param {Object} patternData - Dati del pattern
   */
  const createPattern = async (patternData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const newPattern = await PatternService.createPattern(patternData);
      // Aggiorna la lista dei pattern
      loadPatterns(currentPage, pageSize);
      return newPattern;
    } catch (err) {
      console.error('Errore nella creazione del pattern:', err);
      setError(err.response?.data?.detail || 'Errore nella creazione del pattern');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Aggiorna un pattern esistente
   * @param {number} id - ID del pattern
   * @param {Object} patternData - Nuovi dati del pattern
   */
  const updatePattern = async (id, patternData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedPattern = await PatternService.updatePattern(id, patternData);
      
      // Se il pattern corrente è quello aggiornato, aggiornalo
      if (currentPattern && currentPattern.id === id) {
        setCurrentPattern(updatedPattern);
      }
      
      // Aggiorna la lista dei pattern
      loadPatterns(currentPage, pageSize);
      
      return updatedPattern;
    } catch (err) {
      console.error(`Errore nell'aggiornamento del pattern ${id}:`, err);
      setError(err.response?.data?.detail || 'Errore nell\'aggiornamento del pattern');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Elimina un pattern
   * @param {number} id - ID del pattern da eliminare
   */
  const deletePattern = async (id) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await PatternService.deletePattern(id);
      
      // Se il pattern corrente è quello eliminato, resettalo
      if (currentPattern && currentPattern.id === id) {
        setCurrentPattern(null);
      }
      
      // Aggiorna la lista dei pattern
      loadPatterns(currentPage, pageSize);
      
      return true;
    } catch (err) {
      console.error(`Errore nell'eliminazione del pattern ${id}:`, err);
      setError(err.response?.data?.detail || 'Errore nell\'eliminazione del pattern');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Ottiene statistiche sui pattern
   */
  const getPatternStats = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const stats = await PatternService.getPatternStats();
      return stats;
    } catch (err) {
      console.error('Errore nel caricamento delle statistiche:', err);
      setError(err.response?.data?.detail || 'Errore nel caricamento delle statistiche');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Ottiene pattern correlati a un pattern specifico
   * @param {number} id - ID del pattern di riferimento
   * @param {number} limit - Numero massimo di pattern correlati
   */
  const getRelatedPatterns = async (id, limit = 5) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const relatedPatterns = await PatternService.getRelatedPatterns(id, limit);
      return relatedPatterns;
    } catch (err) {
      console.error(`Errore nel caricamento dei pattern correlati a ${id}:`, err);
      setError(err.response?.data?.detail || 'Errore nel caricamento dei pattern correlati');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Cambia la pagina corrente
   * @param {number} page - Pagina da impostare
   */
  const changePage = (page) => {
    loadPatterns(page, pageSize);
  };

  /**
   * Cambia la dimensione della pagina
   * @param {number} size - Dimensione della pagina
   */
  const changePageSize = (size) => {
    loadPatterns(1, size); // Torna alla prima pagina con la nuova dimensione
  };

  /**
   * Applica filtri alla lista dei pattern
   * @param {Object} newFilters - Nuovi filtri da applicare
   */
  const applyFilters = (newFilters) => {
    loadPatterns(1, pageSize, newFilters); // Torna alla prima pagina con i nuovi filtri
  };

  /**
   * Resetta tutti i filtri
   */
  const resetFilters = () => {
    const emptyFilters = {
      strategy: null,
      mvc_component: null,
      gdpr_id: null,
      pbd_id: null,
      iso_id: null,
      vulnerability_id: null,
      search: null,
    };
    
    setFilters(emptyFilters);
    loadPatterns(1, pageSize, emptyFilters);
  };

  // Carica i pattern all'avvio del provider
  useEffect(() => {
    loadPatterns(1, 10);
  }, [loadPatterns]);

  return (
    <PatternContext.Provider
      value={{
        patterns,
        currentPattern,
        isLoading,
        error,
        totalPatterns,
        currentPage,
        totalPages,
        pageSize,
        filters,
        loadPatterns,
        loadPattern,
        createPattern,
        updatePattern,
        deletePattern,
        getPatternStats,
        getRelatedPatterns,
        changePage,
        changePageSize,
        applyFilters,
        resetFilters,
      }}
    >
      {children}
    </PatternContext.Provider>
  );
};

export default PatternProvider;