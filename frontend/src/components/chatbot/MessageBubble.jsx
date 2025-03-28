// frontend/src/components/chatbot/MessageBubble.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FaRobot, FaUser, FaLink } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const MessageBubble = ({ message }) => {
  // Funzione per renderizzare gli elementi markdown personalizzati
  const customRenderers = {
    // Personalizza il rendering dei link
    a: ({ node, ...props }) => (
      <a className="chat-link" target="_blank" rel="noopener noreferrer" {...props} />
    ),
    // Personalizza il rendering dei blocchi di codice
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      return !inline && language ? (
        <SyntaxHighlighter
          style={docco}
          language={language}
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={inline ? 'inline-code' : 'code-block'} {...props}>
          {children}
        </code>
      );
    }
  };

  // Determina il tipo di link in base al contenuto del messaggio
  const getSourceLink = () => {
    if (message.source === 'pattern' && message.pattern_id) {
      return (
        <Link to={`/patterns/${message.pattern_id}`} className="source-link">
          <FaLink />
          <span>Vedi pattern completo</span>
        </Link>
      );
    } else if (message.source === 'gdpr' && message.article_number) {
      return (
        <Link to={`/gdpr/${message.article_number}`} className="source-link">
          <FaLink />
          <span>Vedi articolo GDPR</span>
        </Link>
      );
    }
    
    return null;
  };

  return (
    <div className={`message ${message.sender}`}>
      <div className="message-avatar">
        {message.sender === 'user' ? <FaUser /> : <FaRobot />}
      </div>
      
      <div className="message-content-wrapper">
        <div className="message-content">
          {message.sender === 'bot' ? (
            <ReactMarkdown components={customRenderers}>
              {message.content}
            </ReactMarkdown>
          ) : (
            <p>{message.content}</p>
          )}
        </div>
        
        {/* Link alle fonti, se presenti */}
        {message.sender === 'bot' && message.source && message.source !== 'chatbot' && (
          <div className="message-source">
            {getSourceLink()}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;