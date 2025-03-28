// frontend/src/pages/gdpr/GDPRPage.jsx
import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FaShieldAlt, FaSearch, FaChevronDown, FaChevronUp, FaExclamationTriangle } from 'react-icons/fa';
import axios from 'axios';

const GDPRPage = () => {
  const { articleNumber } = useParams();
  const navigate = useNavigate();
  
  // Stato per gli articoli GDPR
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  // Stato per l'articolo selezionato
  const [selectedArticle, setSelectedArticle] = useState(null);
  
  // Stato per ricerca
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredArticles, setFilteredArticles] = useState([]);
  
  // Stato per visualizzazione
  const [expandedCategories, setExpandedCategories] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Carica gli articoli GDPR all'avvio
  useEffect(() => {
    const fetchArticles = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await axios.get('/api/gdpr/articles');
        setArticles(response.data);
        
        // Estrai categorie uniche
        const uniqueCategories = [...new Set(response.data.map(article => article.category))];
        setCategories(uniqueCategories);
        
        // Inizializza categorie espanse
        const initialExpanded = {};
        uniqueCategories.forEach(category => {
          initialExpanded[category] = true;
        });
        setExpandedCategories(initialExpanded);
        
        // Se c'è un numero di articolo nei parametri, carica quell'articolo
        if (articleNumber) {
          const article = response.data.find(a => a.number === articleNumber);
          if (article) {
            setSelectedArticle(article);
            // Imposta la categoria dell'articolo come selezionata
            if (article.category) {
              setSelectedCategory(article.category);
            }
          }
        }
      } catch (err) {
        console.error('Errore nel caricamento degli articoli GDPR:', err);
        setError('Si è verificato un errore nel caricamento degli articoli GDPR. Riprova più tardi.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchArticles();
  }, [articleNumber]);
  
  // Filtra gli articoli quando cambiano i filtri
  useEffect(() => {
    let filtered = articles;
    
    // Filtra per categoria
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(article => article.category === selectedCategory);
    }
    
    // Filtra per termine di ricerca
    if (searchTerm) {
      const lowerSearchTerm = searchTerm.toLowerCase();
      filtered = filtered.filter(article => 
        article.title.toLowerCase().includes(lowerSearchTerm) ||
        article.content.toLowerCase().includes(lowerSearchTerm) ||
        article.number.toLowerCase().includes(lowerSearchTerm)
      );
    }
    
    setFilteredArticles(filtered);
  }, [articles, selectedCategory, searchTerm]);
  
  // Toggle espansione categoria
  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };
  
  // Seleziona un articolo
  const handleSelectArticle = (article) => {
    setSelectedArticle(article);
    // Aggiorna l'URL
    navigate(`/gdpr/${article.number}`);
  };
  
  // Cambia la categoria selezionata
  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
  };
  
  // Cambia termine di ricerca
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };
  
  // Funzione per raggruppare gli articoli per categoria
  const getArticlesByCategory = () => {
    const grouped = {};
    
    categories.forEach(category => {
      grouped[category] = filteredArticles.filter(article => article.category === category);
    });
    
    return grouped;
  };
  
  // Se sta caricando, mostra indicatore di caricamento
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento articoli GDPR in corso...</p>
      </div>
    );
  }
  
  // Se c'è un errore, mostra messaggio di errore
  if (error) {
    return (
      <div className="error-container">
        <FaExclamationTriangle className="error-icon" />
        <h2>Si è verificato un errore</h2>
        <p>{error}</p>
        <button className="button primary" onClick={() => window.location.reload()}>
          Riprova
        </button>
      </div>
    );
  }
  
  // Articoli raggruppati per categoria
  const groupedArticles = getArticlesByCategory();
  
  return (
    <div className="gdpr-page">
      <div className="page-header">
        <div className="header-content">
          <h1>General Data Protection Regulation (GDPR)</h1>
          <p>Esplora gli articoli del Regolamento Generale sulla Protezione dei Dati dell'UE</p>
        </div>
      </div>
      
      <div className="gdpr-container">
        <div className="gdpr-sidebar">
          <div className="sidebar-search">
            <div className="search-input-container">
              <FaSearch className="search-icon" />
              <input 
                type="text" 
                value={searchTerm} 
                onChange={handleSearch} 
                placeholder="Cerca articoli..." 
                className="search-input"
              />
            </div>
          </div>
          
          <div className="sidebar-filters">
            <select 
              value={selectedCategory} 
              onChange={handleCategoryChange}
              className="category-select"
            >
              <option value="all">Tutte le categorie</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
          
          <div className="articles-list">
            {Object.entries(groupedArticles).map(([category, articles]) => (
              <div key={category} className="category-group">
                <div 
                  className="category-header"
                  onClick={() => toggleCategory(category)}
                >
                  <h3>{category}</h3>
                  {expandedCategories[category] ? <FaChevronUp /> : <FaChevronDown />}
                </div>
                
                {expandedCategories[category] && (
                  <ul className="category-articles">
                    {articles.map(article => (
                      <li 
                        key={article.id} 
                        className={`article-item ${selectedArticle?.id === article.id ? 'active' : ''}`}
                        onClick={() => handleSelectArticle(article)}
                      >
                        <FaShieldAlt className="article-icon" />
                        <div className="article-info">
                          <span className="article-number">Art. {article.number}</span>
                          <span className="article-title">{article.title}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
            
            {filteredArticles.length === 0 && (
              <div className="no-articles">
                <p>Nessun articolo trovato. Prova a modificare i filtri di ricerca.</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="gdpr-content">
          {selectedArticle ? (
            <div className="article-detail">
              <div className="article-header">
                <h2>
                  <span className="article-number">Articolo {selectedArticle.number}:</span>
                  {selectedArticle.title}
                </h2>
                <span className="article-category">{selectedArticle.category}</span>
              </div>
              
              <div className="article-body">
                {selectedArticle.content.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
              
              {selectedArticle.summary && (
                <div className="article-summary">
                  <h3>Sintesi</h3>
                  <p>{selectedArticle.summary}</p>
                </div>
              )}
              
              {/* Sezione pattern correlati */}
              {selectedArticle.patterns && selectedArticle.patterns.length > 0 && (
                <div className="related-patterns">
                  <h3>Pattern correlati</h3>
                  <ul className="related-patterns-list">
                    {selectedArticle.patterns.map(pattern => (
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
                </div>
              )}
            </div>
          ) : (
            <div className="article-placeholder">
              <FaShieldAlt className="placeholder-icon" />
              <h2>Seleziona un articolo</h2>
              <p>Seleziona un articolo dalla lista per visualizzarne i dettagli</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GDPRPage;