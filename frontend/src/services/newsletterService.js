// frontend/src/services/newsletterService.js
import axios from 'axios';

/**
 * Iscrive un utente alla newsletter
 * @param {string} email - Email da iscrivere
 * @returns {Promise<Object>} - Risultato dell'operazione
 */
export const subscribeNewsletter = async (email) => {
  try {
    const response = await axios.post('/api/newsletter/subscribe', { email });
    return response.data;
  } catch (error) {
    console.error('Errore iscrizione newsletter:', error);
    throw error;
  }
};

/**
 * Verifica un'iscrizione alla newsletter tramite token
 * @param {string} email - Email da verificare
 * @param {string} token - Token di verifica
 * @returns {Promise<Object>} - Risultato dell'operazione
 */
export const verifyNewsletterSubscription = async (email, token) => {
  try {
    const response = await axios.post('/api/newsletter/verify', { email, token });
    return response.data;
  } catch (error) {
    console.error('Errore verifica iscrizione:', error);
    throw error;
  }
};

/**
 * Ottiene lo stato di un'iscrizione alla newsletter
 * @param {string} email - Email da verificare
 * @returns {Promise<Object>} - Stato dell'iscrizione
 */
export const getNewsletterStatus = async (email) => {
  try {
    const response = await axios.get(`/api/newsletter/status?email=${encodeURIComponent(email)}`);
    return response.data;
  } catch (error) {
    console.error('Errore controllo stato iscrizione:', error);
    throw error;
  }
};

/**
 * Cancella un'iscrizione alla newsletter
 * @param {string} email - Email da disiscrivere
 * @returns {Promise<Object>} - Risultato dell'operazione
 */
export const unsubscribeNewsletter = async (email) => {
  try {
    const response = await axios.post('/api/newsletter/unsubscribe', { email });
    return response.data;
  } catch (error) {
    console.error('Errore cancellazione iscrizione:', error);
    throw error;
  }
};