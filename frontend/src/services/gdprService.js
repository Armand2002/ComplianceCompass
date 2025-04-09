import api from './api';

/**
 * Service for GDPR article operations
 */
const GDPRService = {
  /**
   * Retrieves all GDPR articles with error handling
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} - Articles data or empty object on error
   */
  getArticles: async (params = {}) => {
    try {
      const response = await api.get('/gdpr/articles', { params });
      return response.data?.data || { items: [], total: 0 };
    } catch (error) {
      console.error('Error fetching GDPR articles:', error);
      // Return empty data structure to prevent downstream errors
      return { items: [], total: 0 };
    }
  },
  
  getArticleById: async (id) => {
    try {
      const response = await api.get(`/gdpr/articles/${id}`);
      return response.data?.data;
    } catch (error) {
      console.error(`Error fetching GDPR article ${id}:`, error);
      return null;
    }
  },
  
  getArticleByNumber: async (number) => {
    try {
      const response = await api.get(`/gdpr/articles/number/${number}`);
      return response.data?.data;
    } catch (error) {
      console.error(`Error fetching GDPR article ${number}:`, error);
      return null;
    }
  }
};

export default GDPRService;