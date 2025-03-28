// frontend/src/components/chatbot/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { FaPaperPlane, FaRobot, FaUser, FaLink, FaTimes, FaChevronDown } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import ChatbotService from '../../api/chatbotService';
import MessageBubble from './MessageBubble';
import SuggestionList from './SuggestionList';

const ChatInterface = () => {
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
  // Stato per mostrare la barra di introduzione
  const [showIntroBar, setShowIntroBar] = useState(true);

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

  // Effetto per ripristinare la conversazione dal localStorage all'avvio
  useEffect(() => {
    const savedConversation = localStorage.getItem('chatConversation');
    if (savedConversation) {
      try {
        const parsedConversation = JSON.parse(savedConversation);
        setConversation(parsedConversation);
      } catch (err) {
        console.error('Errore nel ripristino della conversazione:', err);
        localStorage.removeItem('chatConversation');
      }
    } else {
      // Se non c'è una conversazione salvata, aggiungi un messaggio di benvenuto
      setConversation([
        {
          id: Date.now(),
          content: "Ciao! Sono l'assistente virtuale di Compliance Compass. Come posso aiutarti oggi con privacy e conformità?",
          sender: 'bot',
        }
      ]);
    }
  }, []);

  // Effetto per salvare la conversazione nel localStorage quando cambia
  useEffect(() => {
    if (conversation.length > 0) {
      localStorage.setItem('chatConversation', JSON.stringify(conversation));
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
        setShowSuggestions(patternSuggestions.length > 0);
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
  const handleSuggestionClick = (suggestion) => {
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

**Strategia:** ${suggestion.strategy}
**Componente MVC:** ${suggestion.mvc_component}
      `,
      sender: 'bot',
      source: 'pattern',
      pattern_id: suggestion.id,
      pattern_title: suggestion.title,
    };

    setConversation(prev => [...prev, botMessage]);
  };

  // Funzione per eliminare la conversazione
  const clearConversation = () => {
    // Mostra dialogo di conferma
    if (window.confirm('Sei sicuro di voler eliminare tutta la conversazione?')) {
      // Aggiungi solo il messaggio di benvenuto
      const welcomeMessage = {
        id: Date.now(),
        content: "Ciao! Sono l'assistente virtuale di Compliance Compass. Come posso aiutarti oggi con privacy e conformità?",
        sender: 'bot',
      };
      
      setConversation([welcomeMessage]);
      localStorage.removeItem('chatConversation');
    }
  };

  return (
    <div className="chat-interface">
      {showIntroBar && (
        <div className="chat-intro-bar">
          <div className="intro-content">
            <p>
              Chiedimi informazioni sui Privacy Patterns, sul GDPR o su qualsiasi aspetto della privacy e sicurezza.
            </p>
          </div>
          <button className="close-intro" onClick={() => setShowIntroBar(false)}>
            <FaTimes />
          </button>
        </div>
      )}
      
      <div className="conversation-container" ref={conversationRef}>
        {conversation.map(msg => (
          <MessageBubble 
            key={msg.id} 
            message={msg} 
          />
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
      {showSuggestions && (
        <SuggestionList 
          suggestions={suggestions} 
          onSuggestionClick={handleSuggestionClick} 
        />
      )}
      
      {/* Input area */}
      <div className="input-container">
        <textarea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Scrivi il tuo messaggio..."
          rows="2"
        />
        <div className="chat-buttons">
          <button 
            className="clear-button" 
            onClick={clearConversation}
            title="Cancella conversazione"
          >
            <FaTimes />
          </button>
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

export default ChatInterface;