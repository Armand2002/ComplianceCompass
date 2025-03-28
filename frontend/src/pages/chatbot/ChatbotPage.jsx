import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { FaPaperPlane, FaRobot, FaUser, FaInfoCircle, FaLink } from 'react-icons/fa';
import ChatbotService from '../../api/chatbotService';

const ChatbotPage = () => {
  // Stato per il messaggio corrente
  const [message, setMessage] = useState('');
  // Stato per la cronologia della conversazione
  const [conversation, setConversation] = useState([]);
  // Stato per indicare se il chatbot sta rispondendo
  const [isTyping, setIsTyping] = useState(false);
  // Stato per eventuali errori
  const [error, setError] = useState(null);
  // Stato per i suggerimenti basati sull'input dell'utente
  const [suggestions, setSuggestions] = useState([]);
  // Stato per mostrare i suggerimenti
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Riferimento al contenitore della conversazione per lo scroll automatico
  const conversationRef = useRef(null);
  // Riferimento all'input per sfocarlo dopo l'invio
  const inputRef = useRef(null);
  // Timeout per i suggerimenti
  const suggestionsTimeoutRef = useRef(null);

  // Effetto per lo scroll automatico quando la conversazione cambia
  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
  }, [conversation]);

  // Effetto per ottenere suggerimenti mentre l'utente digita
  useEffect(() => {
    // Cancella il timeout esistente
    if (suggestionsTimeoutRef.current) {
      clearTimeout(suggestionsTimeoutRef.current);
    }

    // Se l'input è vuoto o troppo corto, non cercare suggerimenti
    if (!message || message.length < 3) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Imposta un nuovo timeout per evitare troppe richieste durante la digitazione
    suggestionsTimeoutRef.current = setTimeout(async () => {
      try {
        const patternSuggestions = await ChatbotService.getPatternSuggestions(message);
        setSuggestions(patternSuggestions);
        setShowSuggestions(true);
      } catch (err) {
        console.error('Errore nel caricamento dei suggerimenti:', err);
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 500); // 500ms di debounce

    // Pulizia al desmontaggio del componente
    return () => {
      if (suggestionsTimeoutRef.current) {
        clearTimeout(suggestionsTimeoutRef.current);
      }
    };
  }, [message]);

  // Funzione per inviare un messaggio al chatbot
  const sendMessage = async () => {
    if (!message.trim()) return;

    // Aggiungi il messaggio dell'utente alla conversazione
    const userMessage = {
      id: Date.now(),
      content: message,
      sender: 'user',
    };

    // Aggiorna la conversazione
    setConversation(prev => [...prev, userMessage]);
    
    // Resetta l'input
    setMessage('');
    setShowSuggestions(false);
    
    // Indica che il chatbot sta "digitando"
    setIsTyping(true);
    setError(null);

    try {
      // Prepara lo storico della conversazione per l'API
      const conversationHistory = conversation.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content,
      }));

      // Invia il messaggio al chatbot
      const response = await ChatbotService.sendMessage(userMessage.content, conversationHistory);

      // Aggiungi la risposta del chatbot alla conversazione
      const botMessage = {
        id: Date.now() + 1,
        content: response.response,
        sender: 'bot',
        source: response.source,
        pattern_id: response.pattern_id,
        pattern_title: response.pattern_title,
        article_id: response.article_id,
        article_number: response.article_number,
      };

      setConversation(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Errore nella comunicazione con il chatbot:', err);
      setError('Si è verificato un errore nella comunicazione con il chatbot. Riprova più tardi.');
    } finally {
      setIsTyping(false);
    }
  };

  // Funzione per gestire l'invio con il tasto Invio
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Funzione per selezionare un suggerimento
  const selectSuggestion = (suggestion) => {
    // Aggiungi un messaggio che indica che l'utente ha cliccato su un pattern
    const userMessage = {
      id: Date.now(),
      content: `Mostrami informazioni sul pattern "${suggestion.title}"`,
      sender: 'user',
    };

    setConversation(prev => [...prev, userMessage]);
    setMessage('');
    setShowSuggestions(false);
    
    // Aggiungi una "risposta" immediata con le informazioni sul pattern
    const botMessage = {
      id: Date.now() + 1,
      content: `
## Pattern: ${suggestion.title}

${suggestion.description}

Strategia: ${suggestion.strategy}

[Vedi dettagli completi del pattern](/patterns/${suggestion.id})
      `,
      sender: 'bot',
      source: 'pattern',
      pattern_id: suggestion.id,
      pattern_title: suggestion.title,
    };

    setConversation(prev => [...prev, botMessage]);
  };

  // Funzione per creare il markup di un messaggio
  const renderMessage = (message) => {
    // Formatta i link se presenti
    const formatLinks = (text) => {
      // Converte markdown links in JSX
      if (message.sender === 'bot') {
        // Gestisci i link ai pattern
        if (message.pattern_id) {
          return text.replace(
            /\[Vedi dettagli completi del pattern\]\(\/patterns\/\d+\)/g,
            `<Link to="/patterns/${message.pattern_id}" class="chatbot-link"><FaLink /> Vedi dettagli completi</Link>`
          );
        }
        
        // Gestisci i link agli articoli GDPR
        if (message.article_id) {
          return text.replace(
            /\[Vedi articolo GDPR\]\(\/gdpr\/[^)]+\)/g,
            `<Link to="/gdpr/${message.article_number}" class="chatbot-link"><FaLink /> Vedi articolo GDPR</Link>`
          );
        }
      }
      
      return text;
    };
    
    // Converti il testo con markdown in HTML
    const formattedText = formatLinks(message.content);
    
    // Supporto di base per markdown
    const convertMarkdown = (text) => {
      if (message.sender !== 'bot') return text;
      
      let formatted = text
        // Titoli
        .replace(/## (.*?)$/gm, '<h3>$1</h3>')
        .replace(/### (.*?)$/gm, '<h4>$1</h4>')
        // Grassetto
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Corsivo
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // List items
        .replace(/- (.*?)$/gm, '<li>$1</li>')
        // Nuove linee
        .replace(/\n/g, '<br />');
      
      return formatted;
    };
    
    return (
      <div 
        className={`message-content ${message.sender}`} 
        dangerouslySetInnerHTML={{ __html: convertMarkdown(formattedText) }}
      />
    );
  };

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
        
        <div className="conversation-container" ref={conversationRef}>
          {/* Messaggio di benvenuto */}
          {conversation.length === 0 && (
            <div className="message bot">
              <div className="message-avatar">
                <FaRobot />
              </div>
              <div className="message-content">
                <p>Ciao! Sono l'assistente virtuale di Compliance Compass. Come posso aiutarti oggi?</p>
              </div>
            </div>
          )}
          
          {/* Conversazione */}
          {conversation.map(msg => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              <div className="message-avatar">
                {msg.sender === 'user' ? <FaUser /> : <FaRobot />}
              </div>
              {renderMessage(msg)}
              {msg.sender === 'bot' && msg.source !== 'chatbot' && (
                <div className="message-source">
                  {msg.source === 'pattern' && msg.pattern_id && (
                    <Link to={`/patterns/${msg.pattern_id}`} className="source-link">
                      Vedi pattern completo
                    </Link>
                  )}
                  {msg.source === 'gdpr' && msg.article_id && (
                    <Link to={`/gdpr/${msg.article_number}`} className="source-link">
                      Vedi articolo GDPR
                    </Link>
                  )}
                </div>
              )}
            </div>
          ))}
          
          {/* Indicatore "sta scrivendo" */}
          {isTyping && (
            <div className="message bot typing">
              <div className="message-avatar">
                <FaRobot />
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          {/* Messaggio di errore */}
          {error && (
            <div className="message error">
              <div className="message-content">
                <p>{error}</p>
              </div>
            </div>
          )}
        </div>
        
        {/* Suggerimenti */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="suggestions-container">
            <h3>Pattern suggeriti:</h3>
            <div className="suggestions-list">
              {suggestions.map(suggestion => (
                <button
                  key={suggestion.id}
                  className="suggestion-item"
                  onClick={() => selectSuggestion(suggestion)}
                >
                  <span className="suggestion-title">{suggestion.title}</span>
                  <span className={`suggestion-strategy ${suggestion.strategy.toLowerCase()}`}>
                    {suggestion.strategy}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Input area */}
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Scrivi il tuo messaggio..."
            rows="3"
          />
          <button 
            className="send-button" 
            onClick={sendMessage}
            disabled={!message.trim() || isTyping}
          >
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;