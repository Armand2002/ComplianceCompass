// frontend/src/pages/gdpr/GDPRPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GDPRService from '../../services/gdprService';
import './GDPRPage.scss';

const GDPRPage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        // Usa il servizio centralizzato invece di axios direttamente
        const data = await GDPRService.getArticles();
        setArticles(data.items || []);
        setError(null);
      } catch (err) {
        console.error('Errore nel caricamento degli articoli GDPR:', err);
        setError('Impossibile caricare gli articoli GDPR. Riprova più tardi.');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  const handleArticleClick = (number) => {
    navigate(`/gdpr/articles/${number}`);
  };

  return (
    <div className="gdpr-page">
      <div className="page-header">
        <h1>Il Regolamento Generale sulla Protezione dei Dati (GDPR)</h1>
        <p className="subtitle">
          Esplora gli articoli del GDPR e la loro applicazione nello sviluppo software
        </p>
      </div>

      <div className="gdpr-intro">
        <p>
          Il Regolamento Generale sulla Protezione dei Dati (GDPR) è una normativa dell'Unione Europea che regola il trattamento dei dati personali dei cittadini dell'UE. Entrato in vigore il 25 maggio 2018, il GDPR stabilisce regole rigorose per la raccolta, l'archiviazione e il trattamento dei dati personali.
        </p>
        <p>
          In questa sezione puoi trovare informazioni dettagliate su ogni articolo del GDPR e su come implementare soluzioni software conformi.
        </p>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Caricamento articoli GDPR...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Riprova</button>
        </div>
      ) : (
        <div className="gdpr-articles-container">
          <h2>Articoli GDPR</h2>
          <div className="gdpr-articles-grid">
            {articles.length > 0 ? (
              articles.map((article) => (
                <div 
                  key={article.id} 
                  className="gdpr-article-card"
                  onClick={() => handleArticleClick(article.number)}
                >
                  <h3>Articolo {article.number}</h3>
                  <h4>{article.title}</h4>
                  <p>{article.summary}</p>
                  <div className="card-footer">
                    <span className="category">{article.category}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>Nessun articolo GDPR disponibile al momento.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GDPRPage;