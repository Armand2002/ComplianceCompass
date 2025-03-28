import api from './axios';

/**
 * Servizio per la gestione dei Privacy Patterns
 */
const PatternService = {
  /**
   * Ottiene la lista dei pattern con paginazione e filtri
   * @param {Object} options - Opzioni di ricerca e paginazione
   * @returns {Promise} - Promise con i dati di risposta
   */
  getPatterns: async (options = {}) => {
    const { 
      page = 1, 
      limit = 10, 
      strategy, 
      mvc_component, 
      gdpr_id, 
      pbd_id, 
      iso_id, 
      vulnerability_id, 
      search 
    } = options;
    
    // Calcola lo skip per la paginazione
    const skip = (page - 1) * limit;
    
    // Costruisci i parametri della query
    let params = { skip, limit };
    
    // Aggiungi i filtri se presenti
    if (strategy) params.strategy = strategy;
    if (mvc_component) params.mvc_component = mvc_component;
    if (gdpr_id) params.gdpr_id = gdpr_id;
    if (pbd_id) params.pbd_id = pbd_id;
    if (iso_id) params.iso_id = iso_id;
    if (vulnerability_id) params.vulnerability_id = vulnerability_id;
    if (search) params.search = search;
    
    const response = await api.get('/patterns/', { params });
    return response.data;
  },
  
  /**
   * Ottiene un pattern specifico per ID
   * @param {number} id - ID del pattern
   * @returns {Promise} - Promise con i dati di risposta
   */
  getPattern: async (id) => {
    const response = await api.get(`/patterns/${id}`);
    return response.data;
  },
  
  /**
   * Crea un nuovo pattern
   * @param {Object} patternData - Dati del pattern da creare
   * @returns {Promise} - Promise con i dati di risposta
   */
  createPattern: async (patternData) => {
    const response = await api.post('/patterns/', patternData);
    return response.data;
  },
  
  /**
   * Aggiorna un pattern esistente
   * @param {number} id - ID del pattern da aggiornare
   * @param {Object} patternData - Nuovi dati del pattern
   * @returns {Promise} - Promise con i dati di risposta
   */
  updatePattern: async (id, patternData) => {
    const response = await api.put(`/patterns/${id}`, patternData);
    return response.data;
  },
  
  /**
   * Elimina un pattern
   * @param {number} id - ID del pattern da eliminare
   * @returns {Promise} - Promise con i dati di risposta
   */
  deletePattern: async (id) => {
    const response = await api.delete(`/patterns/${id}`);
    return response.data;
  },
  
  /**
   * Ottiene statistiche sui pattern
   * @returns {Promise} - Promise con i dati di risposta
   */
  getPatternStats: async () => {
    const response = await api.get('/patterns/stats');
    return response.data;
  },
  
  /**
   * Ottiene pattern per strategia
   * @param {string} strategy - Strategia da filtrare
   * @returns {Promise} - Promise con i dati di risposta
   */
  getPatternsByStrategy: async (strategy) => {
    const response = await api.get(`/patterns/by-strategy/${strategy}`);
    return response.data;
  },
  
  /**
   * Ottiene pattern per componente MVC
   * @param {string} component - Componente MVC da filtrare
   * @returns {Promise} - Promise con i dati di risposta
   */
  getPatternsByMVC: async (component) => {
    const response = await api.get(`/patterns/by-mvc/${component}`);
    return response.data;
  },
  
  /**
   * Ottiene pattern correlati a un pattern specifico
   * @param {number} id - ID del pattern di riferimento
   * @param {number} limit - Numero massimo di pattern correlati
   * @returns {Promise} - Promise con i dati di risposta
   */
  getRelatedPatterns: async (id, limit = 5) => {
    const response = await api.get(`/patterns/related/${id}`, { params: { limit } });
    return response.data;
  },
};

export default PatternService;