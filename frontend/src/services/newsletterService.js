// frontend/src/services/newsletterService.js
/**
 * Servizio per la gestione delle operazioni relative alla newsletter
 */

/**
 * Iscrive un'email alla newsletter
 * @param {string} email - Email da iscrivere
 * @returns {Promise<Object>} Risposta dal server
 */
export const subscribeNewsletter = async (email) => {
  try {
    const response = await fetch('/api/newsletter/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Errore durante l\'iscrizione alla newsletter');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Newsletter subscription error:', error);
    throw error;
  }
};

/**
 * Verifica un'iscrizione alla newsletter tramite token
 * @param {string} email - Email da verificare
 * @param {string} token - Token di verifica
 * @returns {Promise<Object>} Risposta dal server
 */
export const verifyNewsletterSubscription = async (email, token) => {
  try {
    const response = await fetch(`/api/newsletter/verify?email=${encodeURIComponent(email)}&token=${encodeURIComponent(token)}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Errore durante la verifica dell\'iscrizione');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Newsletter verification error:', error);
    throw error;
  }
};

/**
 * Cancella un'iscrizione alla newsletter
 * @param {string} email - Email da disiscrivere
 * @returns {Promise<Object>} Risposta dal server
 */
export const unsubscribeNewsletter = async (email) => {
  try {
    const response = await fetch(`/api/newsletter/unsubscribe?email=${encodeURIComponent(email)}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Errore durante la cancellazione dell\'iscrizione');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Newsletter unsubscribe error:', error);
    throw error;
  }
};

/**
 * Verifica lo stato di un'iscrizione alla newsletter
 * @param {string} email - Email da verificare
 * @returns {Promise<Object>} Risposta dal server con lo stato dell'iscrizione
 */
export const getNewsletterStatus = async (email) => {
  try {
    const response = await fetch(`/api/newsletter/status?email=${encodeURIComponent(email)}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Errore durante la verifica dello stato');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Newsletter status check error:', error);
    throw error;
  }
};