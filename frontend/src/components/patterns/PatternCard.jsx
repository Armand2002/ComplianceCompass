import React from 'react';
import { Link } from 'react-router-dom';
import { FaShieldAlt, FaCode, FaRegClock } from 'react-icons/fa';
import { format } from 'date-fns';
import { it } from 'date-fns/locale';

/**
 * Componente che visualizza un pattern in formato card
 * @param {Object} props - Props del componente
 * @param {Object} props.pattern - Dati del pattern
 */
const PatternCard = ({ pattern }) => {
  // Calcola la data formattata
  const formattedDate = pattern.updated_at 
    ? format(new Date(pattern.updated_at), 'dd MMMM yyyy', { locale: it })
    : '';
  
  // Ottieni il primo articolo GDPR (se presente)
  const firstGdprArticle = pattern.gdpr_articles && pattern.gdpr_articles.length > 0
    ? pattern.gdpr_articles[0]
    : null;
  
  // Determina il colore del badge della strategia
  const getStrategyColor = (strategy) => {
    const strategyColors = {
      'Minimize': 'blue',
      'Hide': 'purple',
      'Separate': 'orange',
      'Aggregate': 'green',
      'Inform': 'teal',
      'Control': 'indigo',
      'Enforce': 'red',
      'Demonstrate': 'yellow',
    };
    
    return strategyColors[strategy] || 'gray';
  };
  
  return (
    <div className="pattern-card">
      <div className="pattern-card-header">
        <div className="pattern-card-badges">
          <span className={`strategy-badge ${getStrategyColor(pattern.strategy)}`}>
            {pattern.strategy}
          </span>
          <span className="mvc-badge">
            {pattern.mvc_component}
          </span>
        </div>
        
        <h3 className="pattern-card-title">
          <Link to={`/patterns/${pattern.id}`}>
            {pattern.title}
          </Link>
        </h3>
      </div>
      
      <div className="pattern-card-content">
        <p className="pattern-card-description">
          {pattern.description.length > 150 
            ? `${pattern.description.substring(0, 150)}...` 
            : pattern.description
          }
        </p>
      </div>
      
      <div className="pattern-card-footer">
        <div className="pattern-card-meta">
          {firstGdprArticle && (
            <div className="meta-item">
              <FaShieldAlt />
              <span>GDPR {firstGdprArticle.number}</span>
            </div>
          )}
          
          <div className="meta-item">
            <FaCode />
            <span>{pattern.mvc_component}</span>
          </div>
          
          <div className="meta-item">
            <FaRegClock />
            <span>{formattedDate}</span>
          </div>
        </div>
        
        <Link to={`/patterns/${pattern.id}`} className="card-link">
          Dettagli
        </Link>
      </div>
    </div>
  );
};

export default PatternCard;