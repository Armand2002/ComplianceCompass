import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { FaShieldAlt, FaBook, FaSearch, FaRobot, FaDatabase, FaCode, FaLightbulb } from 'react-icons/fa';
import NewsletterSubscription from '../components/newsletter/NewsletterSubscription';
import '../styles/pages/homepage.scss';

const HomePage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recentPatterns, setRecentPatterns] = useState([]);
  const [statsData, setStatsData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        setIsLoading(true);
        
        // Carica dati dalla API o utilizza dati di esempio se in sviluppo
        const patternsResponse = await axios.get('/api/patterns?limit=4');
        setRecentPatterns(patternsResponse.data.patterns || []);
        
        // Carica statistiche
        const statsResponse = await axios.get('/api/patterns/stats');
        setStatsData(statsResponse.data || {
          "total_patterns": 12,
          "strategies": {
            "Minimize": 5,
            "Inform": 4,
            "Control": 3,
            "Enforce": 2,
            "Demonstrate": 2
          }
        });
      } catch (err) {
        console.error('Errore nel caricamento dei dati homepage:', err);
        setError('Si è verificato un errore nel caricamento dei dati. Riprova più tardi.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchHomeData();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento...</p>
      </div>
    );
  }

  return (
    <div className="homepage-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1>Simplifica la Privacy e la Compliance</h1>
          <p>Esplora pattern, linee guida e strumenti per incorporare la privacy nello sviluppo software</p>
          
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-box">
              <FaSearch className="search-icon" />
              <input 
                type="text" 
                className="search-input"
                placeholder="Cerca pattern, GDPR, tecniche..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button type="submit" className="button primary">Cerca</button>
          </form>
        </div>
      </div>
      
      {/* Feature Boxes */}
      <div className="features-section">
        <div className="features-grid">
          <Link to="/patterns" className="feature-box">
            <div className="feature-icon">
              <FaShieldAlt />
            </div>
            <h3>Privacy Patterns</h3>
            <p>Soluzioni riutilizzabili per problemi comuni di privacy e sicurezza</p>
          </Link>
          
          <Link to="/gdpr" className="feature-box">
            <div className="feature-icon">
              <FaBook />
            </div>
            <h3>GDPR</h3>
            <p>Esplora il Regolamento Generale sulla Protezione dei Dati</p>
          </Link>
          
          <Link to="/search" className="feature-box">
            <div className="feature-icon">
              <FaSearch />
            </div>
            <h3>Ricerca Avanzata</h3>
            <p>Cerca per categoria, strategia, vulnerabilità e altro</p>
          </Link>
          
          <Link to="/chatbot" className="feature-box">
            <div className="feature-icon">
              <FaRobot />
            </div>
            <h3>Assistente IA</h3>
            <p>Ricevi aiuto personalizzato dal nostro chatbot di supporto</p>
          </Link>
        </div>
      </div>
      
      {/* Sezione Newsletter - NUOVA */}
      <section className="newsletter-section">
        <div className="container">
          <div className="section-header">
            <h2>Rimani Aggiornato</h2>
            <p>Iscriviti alla nostra newsletter per ricevere aggiornamenti sui nuovi pattern 
               di privacy e sulle ultime novità in materia di normative.</p>
          </div>
          
          <div className="newsletter-container">
            <NewsletterSubscription />
          </div>
        </div>
      </section>
      
      {/* Recent Patterns Section */}
      <div className="recent-patterns-section">
        <h2>Pattern Recenti</h2>
        <div className="pattern-cards-grid">
          {recentPatterns.map(pattern => (
            <div key={pattern.id} className="pattern-card">
              <h3>{pattern.name || pattern.title}</h3>
              <p className="pattern-description">{pattern.summary || pattern.description}</p>
              <div className="pattern-tags">
                <span className="pattern-category">{pattern.strategy}</span>
                {pattern.mvc_component && (
                  <span className="pattern-mvc">{pattern.mvc_component}</span>
                )}
              </div>
              <Link to={`/patterns/${pattern.id}`} className="pattern-link">Esplora Pattern</Link>
            </div>
          ))}
        </div>
        <div className="view-all">
          <Link to="/patterns" className="view-all-link">Visualizza tutti i pattern</Link>
        </div>
      </div>
      
      {/* Stats Section */}
      <div className="stats-section">
        <h2>ComplianceCompass in Numeri</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <FaShieldAlt />
            </div>
            <div className="stat-content">
              <h3>Privacy Patterns</h3>
              <p className="stat-value">{statsData?.total_patterns || 0}</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <FaDatabase />
            </div>
            <div className="stat-content">
              <h3>Articoli GDPR</h3>
              <p className="stat-value">99</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <FaCode />
            </div>
            <div className="stat-content">
              <h3>Strategie</h3>
              <p className="stat-value">{statsData?.strategies ? Object.keys(statsData.strategies).length : 0}</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <FaLightbulb />
            </div>
            <div className="stat-content">
              <h3>Vulnerabilità</h3>
              <p className="stat-value">15</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Call to Action Section */}
      <div className="cta-section">
        <h2>Inizia a Esplorare</h2>
        <p>Scopri come integrare la privacy nei tuoi progetti software</p>
        <div className="cta-buttons">
          <Link to="/patterns" className="button primary">Esplora i Pattern</Link>
          <Link to="/gdpr" className="button secondary">Consulta il GDPR</Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;