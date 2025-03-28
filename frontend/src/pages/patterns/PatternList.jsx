import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FaPlus, FaFilter, FaTimes, FaSearch } from 'react-icons/fa';
import { PatternContext } from '../../context/PatternContext';
import { AuthContext } from '../../context/AuthContext';
import PatternCard from '../../components/patterns/PatternCard';
import Pagination from '../../components/common/Pagination';

const PatternList = () => {
  const { 
    patterns, 
    isLoading, 
    error, 
    totalPatterns, 
    currentPage, 
    totalPages, 
    pageSize, 
    filters,
    loadPatterns, 
    changePage, 
    changePageSize, 
    applyFilters, 
    resetFilters 
  } = useContext(PatternContext);
  
  const { user } = useContext(AuthContext);
  
  // Stato per i filtri locali (che vengono applicati solo al click di "Applica Filtri")
  const [localFilters, setLocalFilters] = useState({
    strategy: filters.strategy || '',
    mvc_component: filters.mvc_component || '',
    search: filters.search || '',
  });
  
  // Stato per il modale dei filtri
  const [filtersModalOpen, setFiltersModalOpen] = useState(false);
  
  // Carica i pattern all'avvio del componente
  useEffect(() => {
    loadPatterns(1, 10);
  }, [loadPatterns]);
  
  // Aggiorna i filtri locali quando cambiano i filtri globali
  useEffect(() => {
    setLocalFilters({
      strategy: filters.strategy || '',
      mvc_component: filters.mvc_component || '',
      search: filters.search || '',
    });
  }, [filters]);
  
  // Gestisce il cambio dei filtri locali
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setLocalFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Applica i filtri
  const handleApplyFilters = () => {
    // Converti valori vuoti in null
    const filtersToApply = Object.fromEntries(
      Object.entries(localFilters).map(([key, value]) => [key, value || null])
    );
    
    applyFilters(filtersToApply);
    setFiltersModalOpen(false);
  };
  
  // Resetta i filtri
  const handleResetFilters = () => {
    resetFilters();
    setFiltersModalOpen(false);
  };
  
  // Verifica se l'utente può creare pattern
  const canCreatePattern = user?.role === 'admin' || user?.role === 'editor';
  
  return (
    <div className="pattern-list-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Privacy Patterns</h1>
          <p>Scopri soluzioni riutilizzabili per problemi comuni di privacy e sicurezza</p>
        </div>
        
        {canCreatePattern && (
          <Link to="/patterns/create" className="button primary">
            <FaPlus />
            <span>Nuovo Pattern</span>
          </Link>
        )}
      </div>
      
      <div className="search-filters-bar">
        <div className="search-input-container">
          <FaSearch className="search-icon" />
          <input 
            type="text" 
            placeholder="Cerca pattern..." 
            value={localFilters.search || ''} 
            name="search"
            onChange={handleFilterChange}
            onKeyPress={(e) => e.key === 'Enter' && handleApplyFilters()}
          />
        </div>
        
        <button 
          className="filter-button"
          onClick={() => setFiltersModalOpen(true)}
        >
          <FaFilter />
          <span>Filtri</span>
          {Object.values(filters).some(v => v !== null && v !== '') && (
            <span className="filters-active-badge">•</span>
          )}
        </button>
      </div>
      
      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Caricamento pattern...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>Si è verificato un errore nel caricamento dei pattern.</p>
          <button onClick={() => loadPatterns(currentPage, pageSize)}>Riprova</button>
        </div>
      ) : patterns.length === 0 ? (
        <div className="empty-state">
          <h3>Nessun pattern trovato</h3>
          <p>Prova a modificare i filtri di ricerca o aggiungine uno nuovo.</p>
          {canCreatePattern && (
            <Link to="/patterns/create" className="button secondary">
              <FaPlus />
              <span>Nuovo Pattern</span>
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="patterns-grid">
            {patterns.map(pattern => (
              <PatternCard key={pattern.id} pattern={pattern} />
            ))}
          </div>
          
          <div className="pagination-container">
            <Pagination 
              currentPage={currentPage} 
              totalPages={totalPages}
              onPageChange={changePage}
              totalItems={totalPatterns}
              pageSize={pageSize}
              onPageSizeChange={changePageSize}
            />
          </div>
        </>
      )}
      
      {/* Modale dei filtri */}
      {filtersModalOpen && (
        <div className="filter-modal-overlay">
          <div className="filter-modal">
            <div className="filter-modal-header">
              <h2>Filtri</h2>
              <button 
                className="close-button"
                onClick={() => setFiltersModalOpen(false)}
              >
                <FaTimes />
              </button>
            </div>
            
            <div className="filter-modal-content">
              <div className="filter-group">
                <label htmlFor="strategy">Strategia</label>
                <select 
                  id="strategy" 
                  name="strategy" 
                  value={localFilters.strategy || ''} 
                  onChange={handleFilterChange}
                >
                  <option value="">Tutte le strategie</option>
                  <option value="Minimize">Minimize</option>
                  <option value="Hide">Hide</option>
                  <option value="Separate">Separate</option>
                  <option value="Aggregate">Aggregate</option>
                  <option value="Inform">Inform</option>
                  <option value="Control">Control</option>
                  <option value="Enforce">Enforce</option>
                  <option value="Demonstrate">Demonstrate</option>
                </select>
              </div>
              
              <div className="filter-group">
                <label htmlFor="mvc_component">Componente MVC</label>
                <select 
                  id="mvc_component" 
                  name="mvc_component" 
                  value={localFilters.mvc_component || ''} 
                  onChange={handleFilterChange}
                >
                  <option value="">Tutti i componenti</option>
                  <option value="Model">Model</option>
                  <option value="View">View</option>
                  <option value="Controller">Controller</option>
                </select>
              </div>
            </div>
            
            <div className="filter-modal-footer">
              <button 
                className="button secondary"
                onClick={handleResetFilters}
              >
                Reset
              </button>
              <button 
                className="button primary"
                onClick={handleApplyFilters}
              >
                Applica Filtri
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatternList;