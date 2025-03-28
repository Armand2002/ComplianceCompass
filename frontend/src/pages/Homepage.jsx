import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaShieldAlt, FaBook, FaSearch, FaRobot, FaDatabase, FaCode, FaLightbulb } from 'react-icons/fa';

const HomePage = () => {
  const [recentPatterns, setRecentPatterns] = useState([]);
  const [statsData, setStatsData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchHomeData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Mock data per dimostrazione
        setRecentPatterns([
          {
            id: 1,
            title: "Minimizzazione dei dati",
            description: "Principio che prevede la raccolta e l'utilizzo solo dei dati personali strettamente necessari per raggiungere una finalità specifica.",
            strategy: "Minimize",
            mvc_component: "Model"
          },
          {
            id: 2,
            title: "Consenso informato",
            description: "Pattern che garantisce che gli utenti forniscano un consenso libero, specifico, informato e inequivocabile per il trattamento dei loro dati personali.",
            strategy: "Inform",
            mvc_component: "View"
          },
          {
            id: 3,
            title: "Pseudonimizzazione",
            description: "Tecnica che sostituisce gli identificatori diretti con pseudonimi, mantenendo l'utilità dei dati ma riducendo i rischi per la privacy.",
            strategy: "Abstract",
            mvc_component: "Model"
          }
        ]);
        
        // Mock stats
        setStatsData({
          total: 42,
          strategies: {
            "Minimize": 12,
            "Hide": 8,
            "Separate": 6,
            "Aggregate": 5,
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
          <p>Esplora una raccolta completa di pattern, normative e best practice per implementare la privacy by design nei tuoi progetti.</p>
          
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-box">
              <FaSearch className="search-icon" />
              <input
                type="text"
                placeholder="Cerca pattern, articoli GDPR..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
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
      
      {/* Recent Patterns Section */}
      <div className="recent-patterns-section">
        <div className="section-header">
          <h2>Pattern Recenti</h2>
          <Link to="/patterns" className="section-link">Visualizza tutti</Link>
        </div>
        
        <div className="pattern-cards-grid">
          {recentPatterns.length > 0 ? (
            recentPatterns.map(pattern => (
              <div key={pattern.id} className="pattern-card">
                <div className="pattern-card-header">
                  <div className="pattern-card-badges">
                    <span className={`strategy-badge ${pattern.strategy.toLowerCase()}`}>
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
                  <Link to={`/patterns/${pattern.id}`} className="card-link">
                    Dettagli
                  </Link>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>Nessun pattern disponibile.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Quick Stats Section */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <FaShieldAlt />
            </div>
            <div className="stat-content">
              <h3>Pattern Totali</h3>
              <p className="stat-value">{statsData?.total || 0}</p>
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
        <p>Scopri come i Privacy Pattern possono aiutarti a proteggere i dati dei tuoi utenti</p>
        <Link to="/patterns" className="button primary">Esplora Ora</Link>
      </div>
    </div>
  );
};

export default HomePage;