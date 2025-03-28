// frontend/src/components/search/SearchFilters.jsx
import React from 'react';
import { FaTimes } from 'react-icons/fa';

const SearchFilters = ({ filters, onFilterChange, onResetFilters, options }) => {
  // Struttura dati per le sezioni di filtri
  const filterSections = [
    {
      title: 'Strategia',
      name: 'strategy',
      options: options.strategies.map(strategy => ({
        value: strategy.name,
        label: strategy.name
      }))
    },
    {
      title: 'Componente MVC',
      name: 'mvc_component',
      options: options.mvcComponents.map(component => ({
        value: component.name,
        label: component.name
      }))
    },
    {
      title: 'Articoli GDPR',
      name: 'gdpr_id',
      options: options.gdprArticles.map(article => ({
        value: article.id.toString(),
        label: `Art. ${article.number} - ${article.title}`
      }))
    },
    {
      title: 'Principi Privacy by Design',
      name: 'pbd_id',
      options: options.pbdPrinciples.map(principle => ({
        value: principle.id.toString(),
        label: principle.name
      }))
    },
    {
      title: 'Fasi ISO',
      name: 'iso_id',
      options: options.isoPhases.map(phase => ({
        value: phase.id.toString(),
        label: phase.name
      }))
    },
    {
      title: 'Vulnerabilità',
      name: 'vulnerability_id',
      options: options.vulnerabilities.map(vuln => ({
        value: vuln.id.toString(),
        label: `${vuln.name} (${vuln.severity})`
      }))
    }
  ];
  
  // Verifica se ci sono filtri attivi
  const hasActiveFilters = Object.values(filters).some(value => value !== '');
  
  // Handler per il cambio filtro
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange(name, value);
  };
  
  return (
    <div className="search-filters">
      <div className="filters-header">
        <h3>Filtri Avanzati</h3>
        
        {hasActiveFilters && (
          <button className="reset-filters" onClick={onResetFilters}>
            <FaTimes />
            <span>Resetta filtri</span>
          </button>
        )}
      </div>
      
      <div className="filters-grid">
        {filterSections.map(section => (
          <div key={section.name} className="filter-section">
            <label htmlFor={section.name}>{section.title}</label>
            <select 
              id={section.name}
              name={section.name}
              value={filters[section.name]}
              onChange={handleChange}
              className="filter-select"
            >
              <option value="">Tutti</option>
              {section.options.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
      
      <div className="active-filters">
        {hasActiveFilters && (
          <div className="active-filters-list">
            <span className="active-filters-label">Filtri attivi:</span>
            <div className="filter-tags">
              {Object.entries(filters).map(([key, value]) => {
                if (!value) return null;
                
                // Trova la sezione corrispondente
                const section = filterSections.find(s => s.name === key);
                if (!section) return null;
                
                // Trova l'opzione corrispondente
                const option = section.options.find(o => o.value === value);
                if (!option) return null;
                
                return (
                  <div key={key} className="filter-tag">
                    <span className="filter-tag-label">{section.title}: {option.label}</span>
                    <button 
                      className="filter-tag-remove" 
                      onClick={() => onFilterChange(key, '')}
                    >
                      <FaTimes />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchFilters;