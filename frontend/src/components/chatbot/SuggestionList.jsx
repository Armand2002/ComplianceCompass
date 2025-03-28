// frontend/src/components/chatbot/SuggestionList.jsx
import React from 'react';

const SuggestionList = ({ suggestions, onSuggestionClick }) => {
  if (!suggestions || suggestions.length === 0) return null;
  
  return (
    <div className="suggestions-container">
      <h3 className="suggestions-title">Pattern suggeriti:</h3>
      <div className="suggestions-list">
        {suggestions.map(suggestion => (
          <button
            key={suggestion.id}
            className="suggestion-item"
            onClick={() => onSuggestionClick(suggestion)}
          >
            <div className="suggestion-content">
              <span className="suggestion-title">{suggestion.title}</span>
              <p className="suggestion-description">
                {suggestion.description && suggestion.description.length > 100
                  ? `${suggestion.description.substring(0, 100)}...`
                  : suggestion.description}
              </p>
            </div>
            <span className={`suggestion-strategy ${suggestion.strategy.toLowerCase()}`}>
              {suggestion.strategy}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestionList;