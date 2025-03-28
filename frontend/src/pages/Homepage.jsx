import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaShieldAlt, FaBook, FaUsers, FaLightbulb, FaSearch, FaRobot, FaDatabase, FaCode } from 'react-icons/fa';

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
        // Mock data for demo
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
      <div className="flex items-center justify-center p-8">
        <div className="w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
        <p className="ml-4">Caricamento...</p>
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
      <div className="my-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Pattern Recenti</h2>
          <a href="/patterns" className="text-blue-600 hover:underline">Visualizza tutti</a>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recentPatterns.length > 0 ? (
            recentPatterns.map(pattern => (
              <div key={pattern.id} className="bg-white shadow-md rounded-lg overflow-hidden">
                <div className="p-6">
                  <div className="flex gap-2 mb-3">
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {pattern.strategy}
                    </span>
                    <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                      {pattern.mvc_component}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold mb-2">
                    <a href={`/patterns/${pattern.id}`} className="hover:text-blue-600">
                      {pattern.title}
                    </a>
                  </h3>
                  
                  <p className="text-gray-600 text-sm mb-4">
                    {pattern.description.length > 150 
                      ? `${pattern.description.substring(0, 150)}...` 
                      : pattern.description
                    }
                  </p>
                  
                  <a href={`/patterns/${pattern.id}`} className="text-blue-600 hover:underline text-sm">
                    Dettagli →
                  </a>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-3 text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-500">Nessun pattern disponibile.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Quick Stats Section */}
      <div className="my-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white shadow-md rounded-lg p-6 flex items-center">
            <div className="bg-blue-100 p-4 rounded-full mr-4">
              <FaShieldAlt />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Pattern Totali</h3>
              <p className="text-3xl font-bold">{statsData?.total || 0}</p>
            </div>
          </div>
          
          <div className="bg-white shadow-md rounded-lg p-6 flex items-center">
            <div className="bg-blue-100 p-4 rounded-full mr-4">
              <FaDatabase />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Articoli GDPR</h3>
              <p className="text-3xl font-bold">99</p>
            </div>
          </div>
          
          <div className="bg-white shadow-md rounded-lg p-6 flex items-center">
            <div className="bg-blue-100 p-4 rounded-full mr-4">
              <FaCode />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Strategie</h3>
              <p className="text-3xl font-bold">{statsData?.strategies ? Object.keys(statsData.strategies).length : 0}</p>
            </div>
          </div>
          
          <div className="bg-white shadow-md rounded-lg p-6 flex items-center">
            <div className="bg-blue-100 p-4 rounded-full mr-4">
              <FaLightbulb />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Vulnerabilità</h3>
              <p className="text-3xl font-bold">15</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* About Section */}
      <div className="my-12 bg-gray-50 rounded-lg p-8">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Informazioni su Compliance Compass</h2>
          <p className="mb-4">
            Compliance Compass è una piattaforma wiki collaborativa progettata per semplificare 
            la comprensione delle normative tecniche e di sicurezza. Il nostro obiettivo è fornire 
            ai professionisti dell'informatica, agli sviluppatori e ai responsabili della privacy 
            uno strumento completo per navigare nel complesso panorama della conformità 
            alla privacy e alla sicurezza.
          </p>
          <p className="mb-6">
            La piattaforma offre una vasta collezione di Privacy Pattern, un'esplorazione 
            dettagliata del GDPR, e strumenti intelligenti come ricerca avanzata e un assistente 
            basato su AI per aiutarti a trovare rapidamente le informazioni di cui hai bisogno.
          </p>
          
          <div className="flex gap-4">
            <a href="/patterns" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded-lg">Esplora i Pattern</a>
            <a href="/about" className="bg-white hover:bg-gray-100 text-blue-600 border border-blue-600 py-2 px-6 rounded-lg">Scopri di più</a>
          </div>
        </div>
      </div>
      
      {/* Call to Action Section */}
      <div className="my-12 bg-blue-700 text-white text-center py-12 px-4 rounded-lg">
        <h2 className="text-3xl font-bold mb-2">Inizia a Esplorare</h2>
        <p className="text-xl mb-6">Scopri come i Privacy Pattern possono aiutarti a proteggere i dati dei tuoi utenti</p>
        <a href="/patterns" className="bg-white text-blue-700 hover:bg-gray-100 py-3 px-8 rounded-lg font-bold">Esplora Ora</a>
      </div>
    </div>
  );
};

export default HomePage;