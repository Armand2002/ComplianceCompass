import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  FaShieldAlt, 
  FaBook, 
  FaSearch, 
  FaRobot, 
  FaChartBar,
  FaExclamationTriangle,
  FaPlus,
  FaEye,
  FaRegClock
} from 'react-icons/fa';
import { PatternContext } from '../../context/PatternContext';
import { AuthContext } from '../../context/AuthContext';
import PatternService from '../../api/patternService';
import SearchService from '../../api/searchService';

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const { patterns, loadPatterns } = useContext(PatternContext);
  
  // State per statistiche e pattern recenti
  const [stats, setStats] = useState(null);
  const [recentPatterns, setRecentPatterns] = useState([]);
  const [trendingPatterns, setTrendingPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Caricamento dei dati al montaggio del componente
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Carica pattern recenti (ultimi 5)
        await loadPatterns(1, 5);
        
        // Carica statistiche
        const patternStats = await PatternService.getPatternStats();
        
        // Carica pattern di tendenza
        const trending = await SearchService.getTrendingPatterns(5);
        
        setStats(patternStats);
        setTrendingPatterns(trending);
        setRecentPatterns(patterns);
      } catch (err) {
        console.error('Errore nel caricamento dei dati dashboard:', err);
        setError('Si è verificato un errore nel caricamento dei dati. Riprova più tardi.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [loadPatterns]);
  
  // Verifica se l'utente può creare pattern
  const canCreatePattern = user?.role === 'admin' || user?.role === 'editor';
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Caricamento dashboard...</p>
      </div>
    );
  }
  
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
  
  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Dashboard</h1>
          <p>Benvenuto nel Compliance Compass, {user.full_name || user.username}!</p>
        </div>
        
        {canCreatePattern && (
          <Link to="/patterns/create" className="button primary">
            <FaPlus />
            <span>Nuovo Pattern</span>
          </Link>
        )}
      </div>
      
      {/* Statistiche */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <FaBook />
          </div>
          <div className="stat-content">
            <h3>Pattern Totali</h3>
            <p className="stat-value">{stats?.total || 0}</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <FaShieldAlt />
          </div>
          <div className="stat-content">
            <h3>Articoli GDPR</h3>
            <p className="stat-value">45</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <FaSearch />
          </div>
          <div className="stat-content">
            <h3>Ricerche Effettuate</h3>
            <p className="stat-value">127</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <FaRobot />
          </div>
          <div className="stat-content">
            <h3>Richieste al Chatbot</h3>
            <p className="stat-value">83</p>
          </div>
        </div>
      </div>
      
      <div className="dashboard-main">
        {/* Sezione Pattern Recenti */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Pattern Recenti</h2>
            <Link to="/patterns" className="section-link">
              Vedi tutti
            </Link>
          </div>
          
          <div className="dashboard-cards">
            {recentPatterns.length > 0 ? (
              recentPatterns.map(pattern => (
                <div key={pattern.id} className="dash-pattern-card">
                  <div className="dash-pattern-header">
                    <span className={`strategy-badge ${pattern.strategy.toLowerCase()}`}>
                      {pattern.strategy}
                    </span>
                    <h3 className="dash-pattern-title">
                      <Link to={`/patterns/${pattern.id}`}>{pattern.title}</Link>
                    </h3>
                  </div>
                  <p className="dash-pattern-description">
                    {pattern.description.length > 120 
                      ? `${pattern.description.substring(0, 120)}...` 
                      : pattern.description
                    }
                  </p>
                  <div className="dash-pattern-footer">
                    <span className="dash-pattern-meta">
                      <FaRegClock />
                      <span>
                        {new Date(pattern.updated_at).toLocaleDateString('it-IT', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric'
                        })}
                      </span>
                    </span>
                    <Link to={`/patterns/${pattern.id}`} className="dash-pattern-link">
                      <FaEye />
                      <span>Dettagli</span>
                    </Link>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state small">
                <p>Nessun pattern disponibile.</p>
                {canCreatePattern && (
                  <Link to="/patterns/create" className="button secondary small">
                    <FaPlus />
                    <span>Crea il primo pattern</span>
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Colonna destra */}
        <div className="dashboard-sidebar">
          {/* Sezione Pattern di Tendenza */}
          <div className="dashboard-sidebar-section">
            <h2>Pattern Popolari</h2>
            
            {trendingPatterns.length > 0 ? (
              <ul className="trending-patterns-list">
                {trendingPatterns.map(pattern => (
                  <li key={pattern.id} className="trending-pattern-item">
                    <Link to={`/patterns/${pattern.id}`} className="trending-pattern-link">
                      <span className="trending-pattern-title">{pattern.title}</span>
                      <span className={`strategy-badge small ${pattern.strategy.toLowerCase()}`}>
                        {pattern.strategy}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-patterns">Nessun pattern popolare disponibile.</p>
            )}
          </div>
          
          {/* Sezione Distribuzione per Strategia */}
          <div className="dashboard-sidebar-section">
            <h2>Distribuzione Strategie</h2>
            
            {stats && stats.strategies && Object.keys(stats.strategies).length > 0 ? (
              <div className="strategy-distribution">
                {Object.entries(stats.strategies).map(([strategy, count]) => (
                  <div key={strategy} className="distribution-item">
                    <div className="distribution-label">
                      <span className={`strategy-badge small ${strategy.toLowerCase()}`}>
                        {strategy}
                      </span>
                      <span className="distribution-count">{count}</span>
                    </div>
                    <div className="distribution-bar-container">
                      <div 
                        className="distribution-bar"
                        style={{ 
                          width: `${(count / stats.total) * 100}%`,
                          backgroundColor: `var(--strategy-${strategy.toLowerCase()})` 
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">Nessun dato disponibile.</p>
            )}
          </div>
          
          {/* Collegamento al chatbot */}
          <div className="chatbot-promo">
            <div className="promo-icon">
              <FaRobot />
            </div>
            <div className="promo-content">
              <h3>Hai bisogno di aiuto?</h3>
              <p>Prova il nostro assistente virtuale per domande su GDPR e Privacy Pattern.</p>
              <Link to="/chatbot" className="button primary small">
                Vai al Chatbot
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;