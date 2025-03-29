/**
 * Funzioni di validazione per form e input
 */

// Validazione email
export const isValidEmail = (email) => {
  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return regex.test(email);
};

// Validazione password (min 8 caratteri, almeno 1 lettera, 1 numero)
export const isValidPassword = (password) => {
  if (!password || password.length < 8) return false;
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  return hasLetter && hasNumber;
};

// Verifica che due valori siano uguali (es. password e conferma)
export const valuesMatch = (value1, value2) => {
  return value1 === value2;
};

// Validazione URL
export const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Validazione numeri
export const isPositiveNumber = (value) => {
  const num = Number(value);
  return !isNaN(num) && num > 0;
};

// Validazione stringa non vuota
export const isNotEmpty = (value) => {
  return typeof value === 'string' && value.trim().length > 0;
};

// Validazione lunghezza
export const hasMinLength = (value, minLength) => {
  return typeof value === 'string' && value.length >= minLength;
};

export const hasMaxLength = (value, maxLength) => {
  return typeof value === 'string' && value.length <= maxLength;
};