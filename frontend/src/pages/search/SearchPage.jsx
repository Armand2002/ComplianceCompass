// frontend/src/pages/search/SearchPage.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FaSearch, FaFilter, FaTimes, FaChevronDown, FaChevronUp } from 'react-icons/fa';
import axios from 'axios';
import { debounce } from 'lodash';

import SearchFilters from '../../components/search/SearchFilters';
import SearchResults from '../../components/search/SearchResults';
import Pagination from '../../components/common/Pagination';

const SearchPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Estrai query dai parametri URL
  const queryParams = new URLSearchParams(location.search);
  
  // Stato per la ricerca
  const [query, setQuery] = useState(queryParams.get('q') || '');
  const [page, setPage] = useState(parseInt(queryParams.get('page') || '1', 10));
  const [pageSize, setPageSize] = useState(parseInt(queryParams.get('size') || '10', 10));
  
  // Stato per i risultati
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  
  // Stato per i filtri
  const [filters, setFilters] = useState({
    strategy: queryParams.get('strategy') || '',
    mvc_component: queryParams.get('mvc_component') || '',
    gdpr_id: queryParams.get('gdpr_id') || '',
    pbd_id: queryParams.get('pbd_id') || '',
    iso_id: queryParams.get('iso_id') || '',
    vulnerability_id: queryParams.get('vulnerability_id') || ''
  });
  
  // Stato per filtri avanzati
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [filterOptions, setFilterOptions] = useState({
    strategies: [],
    mvcComponents: [],
    gdprArticles: [],
    pbdPrinciples: [],
    isoPhases: [],
    vulnerabilities: []
  });
  
  // Stato per loading e errori
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Stato per autocomplete
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // Funzione debounce per la ricerca
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce((searchParams) => {
      performSearch(searchParams);
    }, 500),
    []
  );
  
  // Carica opzioni di filtro all'avvio
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        // Carica strategie
        const strategiesResponse = await axios.get('/api/patterns/strategies');
        
        // Carica componenti MVC
        const mvcResponse = await axios.get('/api/patterns/mvc-components');
        
        // Carica articoli GDPR
        const gdprResponse = await axios.get('/api/gdpr/articles');
        
        // Carica principi PbD
        const pbdResponse = await axios.get('/api/pbd/principles');
        
        // Carica fasi ISO
        const isoResponse = await axios.get('/api/iso/phases');
        
        // Carica vulnerabilità
        const vulnResponse = await axios.get('/api/vulnerabilities');
        
        setFilterOptions({
          strategies: strategiesResponse.data,
          mvcComponents: mvcResponse.data,
          gdprArticles: gdprResponse.data,
          pbdPrinciples: pbdResponse.data,
          isoPhases: isoResponse.data,
          vulnerabilities: vulnResponse.data
        });
      } catch (err) {
        console.error('Errore nel caricamento delle opzioni di filtro:', err);
      }
    };
    
    fetchFilterOptions();
  }, []);
  
  // Funzione per ottenere suggesti di autocomplete
  const fetchSuggestions = async (searchText) => {
    if (!searchText || searchText.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    try {
      const response = await axios.get('/api/search/autocomplete', {
        params: { q: searchText }
      });
      
      setSuggestions(response.data.suggestions);
      setShowSuggestions(true);
    } catch (err) {
      console.error('Errore nel caricamento dei suggerimenti:', err);
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };
  
  // Effetto per aggiornare la ricerca quando i parametri cambiano
  useEffect(() => {
    // Prepara i parametri di ricerca
    const searchParams = {
      q: query,
      page,
      size: pageSize,
      ...filters
    };
    
    // Aggiorna URL
    updateUrl(searchParams);
    
    // Esegui la ricerca
    debouncedSearch(searchParams);
  }, [query, page, pageSize, filters, debouncedSearch]);
  
  // Funzione per aggiornare l'URL
  const updateUrl = (params) => {
    const urlParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value) {
        urlParams.set(key, value);
      }
    });
    
    navigate({
      pathname: location.pathname,
      search: urlParams.toString()
    }, { replace: true });
  };
  
  // Funzione per eseguire la ricerca
  const performSearch = async (params) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Calcola offset per paginazione
      const skip = (params.page - 1) * params.size;
      
      // Rimuovi parametri vuoti
      const cleanParams = {};
      Object.entries(params).forEach(([key, value]) => {
        if (value) {
          cleanParams[key] = value;
        }
      });
      
      // Sostituisci page e size con skip e limit
      const { page, size, ...restParams } = cleanParams;
      const queryParams = {
        ...restParams,
        skip,
        limit: params.size
      };
      
      // Esegui ricerca
      const response = await axios.get('/api/search/patterns', {
        params: queryParams
      });
      
      // Aggiorna stato
      setResults(response.data.patterns || []);
      setTotalResults(response.data.total || 0);
      setTotalPages(response.data.pages || 1);
    } catch (err) {
      console.error('Errore nella ricerca:', err);
      setError('Si è verificato un errore durante la ricerca. Riprova più tardi.');
      setResults([]);
      setTotalResults(0);
      setTotalPages(1);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handler per il cambio query
  const handleQueryChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    fetchSuggestions(value);
  };
  
  // Handler per il click su un suggerimento
  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.text);
    setShowSuggestions(false);
    // Esegui ricerca immediata
    setPage(1);
  };
  
  // Handler per il reset dei filtri
  const handleResetFilters = () => {
    setFilters({
      strategy: '',
      mvc_component: '',
      gdpr_id: '',
      pbd_id: '',
      iso_id: '',
      vulnerability_id: ''
    });
    setPage(1);
  };
  
  // Handler per il cambio filtri
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    setPage(1);
  };
  
  // Handler per il cambio pagina
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };
  
  // Handler per il cambio dimensione pagina
  const handlePageSizeChange = (newSize) => {
    setPageSize(newSize);
    setPage(1);
  };
  
  return (
    <div className="search-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Ricerca Avanzata</h1>
          <p>Cerca Privacy Patterns, articoli GDPR e altri contenuti</p>
        </div>
      </div>
      
      <div className="search-container">
        <div className="search-bar">
          <div className="search-input-container">
            <FaSearch className="search-icon" />
            <input 
              type="text" 
              value={query} 
              onChange={handleQueryChange} 
              placeholder="Cerca pattern, articoli, principi..." 
              className="search-input"
            />
            {query && (
              <button 
                className="clear-search" 
                onClick={() => setQuery('')}
              >
                <FaTimes />
              </button>
            )}
          </div>
          
          <button 
            className={`filter-toggle ${showAdvancedFilters ? 'active' : ''}`}
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          >
            <FaFilter />
            <span>Filtri</span>
            {showAdvancedFilters ? <FaChevronUp /> : <FaChevronDown />}
          </button>
        </div>
        
        {/* Suggerimenti */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="search-suggestions">
            <ul>
              {suggestions.map(suggestion => (
                <li key={suggestion.id} onClick={() => handleSuggestionClick(suggestion)}>
                  <span className="suggestion-text">{suggestion.text}</span>
                  <span className="suggestion-type">{suggestion.title}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Filtri avanzati */}
        {showAdvancedFilters && (
          <SearchFilters 
            filters={filters}
            onFilterChange={handleFilterChange}
            onResetFilters={handleResetFilters}
            options={filterOptions}
          />
        )}
        
        {/* Risultati di ricerca */}
        <div className="search-results-container">
          <div className="search-results-header">
            {isLoading ? (
              <p>Ricerca in corso...</p>
            ) : (
              <p>
                {totalResults > 0 
                  ? `Trovati ${totalResults} risultati${query ? ` per "${query}"` : ''}`
                  : `Nessun risultato trovato${query ? ` per "${query}"` : ''}`
                }
              </p>
            )}
          </div>
          
          <SearchResults 
            results={results}
            isLoading={isLoading}
            error={error}
            searchTerm={query}
          />
          
          {totalResults > 0 && (
            <div className="pagination-container">
              <Pagination 
                currentPage={page}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                totalItems={totalResults}
                pageSize={pageSize}
                onPageSizeChange={handlePageSizeChange}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchPage;