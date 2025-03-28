import api from './axios';

/**
 * Servizio per la gestione delle ricerche
 */
const SearchService = {
  /**
   * Esegue una ricerca avanzata di pattern
   * @param {Object} searchOptions - Opzioni di ricerca
   * @returns {Promise} - Promise con i dati di risposta
   */
  searchPatterns: async (searchOptions = {}) => {
    const { 
      query, 
      page = 1, 
      limit = 10, 
      strategy, 
      mvc_component, 
      gdpr_id, 
      pbd_id, 
      iso_id, 
      vulnerability_id 
    } = searchOptions;
    
    // Calcola lo skip per la paginazione
    const skip = (page - 1) * limit;
    
    // Costruisci i parametri della query
    let params = { 
      q: query,
      skip,
      limit
    };
    
    // Aggiungi i filtri se presenti
    if (strategy) params.strategy = strategy;
    if (mvc_component) params.mvc_component = mvc_component;
    if (gdpr_id) params.gdpr_id = gdpr_id;
    if (pbd_id) params.pbd_id = pbd_id;
    if (iso_id) params.iso_id = iso_id;
    if (vulnerability_id) params.vulnerability_id = vulnerability_id;
    
    const response = await api.get('/search/patterns', { params });
    return response.data;
  },
  
  /**
   * Ottiene suggerimenti per l'autocompletamento
   * @param {string} query - Query parziale
   * @param {number} limit - Numero massimo di suggerimenti
   * @returns {Promise} - Promise con i dati di risposta
   */
  getAutocompleteSuggestions: async (query, limit = 10) => {
    const response = await api.get('/search/autocomplete', { 
      params: { q: query, limit } 
    });
    return response.data.suggestions;
  },
  
  /**
   * Ottiene i pattern più popolari o di tendenza
   * @param {number} limit - Numero massimo di pattern da restituire
   * @returns {Promise} - Promise con i dati di risposta
   */
  getTrendingPatterns: async (limit = 5) => {
    const response = await api.get('/search/trending', { params: { limit } });
    return response.data.patterns;
  },
};

export default SearchService;