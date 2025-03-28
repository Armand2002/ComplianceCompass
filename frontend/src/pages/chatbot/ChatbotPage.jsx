// frontend/src/pages/chatbot/ChatbotPage.jsx
import React from 'react';
import { FaInfoCircle } from 'react-icons/fa';
import ChatInterface from '../../components/chatbot/ChatInterface';

const ChatbotPage = () => {
  return (
    <div className="chatbot-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Assistente Compliance Compass</h1>
          <p>Chiedimi informazioni sui Privacy Patterns, sul GDPR o su qualsiasi aspetto della privacy e sicurezza.</p>
        </div>
      </div>
      
      <div className="chatbot-container">
        <div className="chatbot-info">
          <FaInfoCircle />
          <p>
            L'assistente può fornirti informazioni sui Privacy Patterns, sul GDPR e sulle pratiche di privacy by design.
            Prova a chiedere cose come "Cos'è un Privacy Pattern?", "Spiegami l'articolo 25 del GDPR" o "Come posso implementare la minimizzazione dei dati?".
          </p>
        </div>
        
        <div className="chat-content">
          <ChatInterface />
        </div>
        
        <div className="chatbot-help">
          <h3>Suggerimenti di domande</h3>
          <div className="question-suggestions">
            <button className="question-suggestion" onClick={() => window.handleSuggestedQuestion("Cosa sono i Privacy Pattern?")}>
              Cosa sono i Privacy Pattern?
            </button>
            <button className="question-suggestion" onClick={() => window.handleSuggestedQuestion("Cosa dice l'articolo 25 del GDPR?")}>
              Cosa dice l'articolo 25 del GDPR?
            </button>
            <button className="question-suggestion" onClick={() => window.handleSuggestedQuestion("Quali sono i principi di Privacy by Design?")}>
              Quali sono i principi di Privacy by Design?
            </button>
            <button className="question-suggestion" onClick={() => window.handleSuggestedQuestion("Suggerisci pattern per implementare la minimizzazione dei dati")}>
              Suggerisci pattern per implementare la minimizzazione dei dati
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Funzione globale per gestire i suggerimenti di domande
// Sarà connessa con il componente ChatInterface tramite window
window.handleSuggestedQuestion = (question) => {
  // Questa funzione verrà sostituita a runtime dal componente ChatInterface
  console.log("Questa funzione dovrebbe essere sovrascritta dal componente ChatInterface");
};

export default ChatbotPage;