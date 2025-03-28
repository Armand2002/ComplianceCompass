import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Componente che visualizza una lista di pattern correlati
 * @param {Object} props - Props del componente
 * @param {Array} props.patterns - Lista di pattern correlati
 */
const RelatedPatterns = ({ patterns }) => {
  if (!patterns || patterns.length === 0) {
    return <p className="no-patterns">Nessun pattern correlato trovato.</p>;
  }

  return (
    <ul className="related-patterns-list">
      {patterns.map(pattern => (
        <li key={pattern.id} className="related-pattern-item">
          <Link to={`/patterns/${pattern.id}`} className="related-pattern-link">
            <div className="related-pattern-info">
              <h4 className="related-pattern-title">{pattern.title}</h4>
              <div className="related-pattern-badges">
                <span className={`strategy-badge small ${pattern.strategy.toLowerCase()}`}>
                  {pattern.strategy}
                </span>
                <span className="mvc-badge small">
                  {pattern.mvc_component}
                </span>
              </div>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
};

export default RelatedPatterns;