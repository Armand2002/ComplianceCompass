import api from './axios';

/**
 * Servizio per la gestione del chatbot
 */
const ChatbotService = {
  /**
   * Invia un messaggio al chatbot e ottiene una risposta
   * @param {string} message - Messaggio dell'utente
   * @param {Array} conversationHistory - Storico della conversazione
   * @returns {Promise} - Promise con i dati di risposta
   */
  sendMessage: async (message, conversationHistory = []) => {
    const response = await api.post('/chatbot/chat', {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  },
  
  /**
   * Ottiene suggerimenti di pattern basati sulla query dell'utente
   * @param {string} query - Query dell'utente
   * @returns {Promise} - Promise con i dati di risposta
   */
  getPatternSuggestions: async (query) => {
    const response = await api.get('/chatbot/suggestions', {
      params: { query },
    });
    return response.data;
  }
};

export default ChatbotService;