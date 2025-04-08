// frontend/src/pages/privacy-by-design/PrivacyByDesignPage.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PrivacyByDesignPage.scss';

const PrivacyByDesignPage = () => {
  const [principles, setPrinciples] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPrinciples = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/privacy-by-design/principles');
        setPrinciples(response.data.items || []);
        setError(null);
      } catch (err) {
        console.error('Errore nel caricamento dei principi Privacy by Design:', err);
        setError('Impossibile caricare i principi. Riprova più tardi.');
      } finally {
        setLoading(false);
      }
    };

    fetchPrinciples();
  }, []);

  // Se l'API non è ancora disponibile, utilizziamo dei dati di esempio
  const placeholderPrinciples = [
    {
      id: 1,
      name: "Proattivo non reattivo",
      description: "Privacy by Design si concentra su misure proattive piuttosto che reattive. Anticipa e previene eventi invasivi della privacy prima che accadano, non aspetta che i rischi si materializzino.",
      examples: [
        "Condurre valutazioni d'impatto sulla privacy prima dello sviluppo",
        "Progettare sistemi che minimizzano la raccolta di dati fin dall'inizio",
        "Implementare protocolli di sicurezza avanzati in fase di progettazione"
      ]
    },
    {
      id: 2,
      name: "Privacy come impostazione predefinita",
      description: "I dati personali sono automaticamente protetti in qualsiasi sistema IT o pratica aziendale. Non è richiesta alcuna azione da parte dell'individuo per proteggere la propria privacy: è integrata nel sistema, per impostazione predefinita.",
      examples: [
        "Opt-in esplicito invece di opt-out per la raccolta dei dati",
        "Configurazioni di privacy restrittive come impostazione predefinita",
        "Raccolta minima dei dati necessari per la funzionalità"
      ]
    },
    {
      id: 3,
      name: "Privacy incorporata nella progettazione",
      description: "La privacy è integrata nella progettazione e nell'architettura dei sistemi IT e nelle pratiche aziendali. Non è aggiunta successivamente ma è componente essenziale della funzionalità principale.",
      examples: [
        "Architetture che separano dati identificativi dai dati operativi",
        "Tecniche di minimizzazione dei dati come parte dell'architettura",
        "Progettazione modulare che permette isolamento dei dati sensibili"
      ]
    },
    {
      id: 4,
      name: "Funzionalità completa",
      description: "Privacy by Design cerca di soddisfare tutti gli interessi e obiettivi legittimi in un paradigma 'somma positiva', non attraverso un approccio di 'somma zero' datato che impone compromessi non necessari.",
      examples: [
        "Sistemi che offrono sicurezza e usabilità senza compromettere la privacy",
        "Interfacce che permettono funzionalità complete con consenso granulare",
        "Meccanismi di autenticazione avanzati che non richiedono eccessivi dati personali"
      ]
    },
    {
      id: 5,
      name: "Sicurezza end-to-end",
      description: "Privacy by Design, incorporato nel sistema prima della raccolta del primo elemento di informazione, si estende in modo sicuro durante l'intero ciclo di vita dei dati coinvolti.",
      examples: [
        "Crittografia dei dati in transito e a riposo",
        "Controlli di accesso granulari basati sui ruoli",
        "Meccanismi di distruzione sicura dei dati al termine del loro ciclo di vita"
      ]
    },
    {
      id: 6,
      name: "Visibilità e trasparenza",
      description: "Privacy by Design assicura a tutti gli stakeholder che qualunque pratica o tecnologia aziendale coinvolta sia operante secondo le promesse e gli obiettivi dichiarati, soggetta a verifica indipendente.",
      examples: [
        "Politiche sulla privacy chiare e comprensibili",
        "Interfacce che mostrano chiaramente quali dati vengono raccolti e come",
        "Audit trail accessibili per le operazioni sui dati personali"
      ]
    },
    {
      id: 7,
      name: "Rispetto per la privacy dell'utente",
      description: "Privacy by Design richiede che gli architetti e gli operatori mantengano al centro gli interessi dell'individuo, offrendo misure come impostazioni predefinite rigide sulla privacy, notifiche appropriate e opzioni facili da usare.",
      examples: [
        "Controlli utente intuitivi per gestire le preferenze di privacy",
        "Meccanismi semplici per accedere, correggere o eliminare i propri dati",
        "Sistemi di consenso che rispettano le scelte dell'utente"
      ]
    }
  ];

  // Se non ci sono dati dall'API, usiamo i dati di esempio
  useEffect(() => {
    if (!loading && principles.length === 0 && !error) {
      setPrinciples(placeholderPrinciples);
    }
  }, [loading, principles, error]);

  return (
    <div className="pbd-page">
      <div className="page-header">
        <h1>Privacy by Design</h1>
        <p className="subtitle">
          Principi fondamentali per incorporare la privacy nello sviluppo dei sistemi informatici
        </p>
      </div>

      <div className="pbd-intro">
        <p>
          Privacy by Design (PbD) è un approccio che consiste nell'incorporare la privacy nel design di sistemi IT, pratiche commerciali e architetture di rete. Sviluppato da Ann Cavoukian, ex Commissario per l'Informazione e la Privacy dell'Ontario, Canada, Privacy by Design si basa sul principio che la privacy non debba essere un elemento aggiunto, ma debba far parte integrante dei sistemi fin dalla loro progettazione.
        </p>
        <p>
          Il GDPR ha reso la Privacy by Design un requisito legale nell'UE attraverso l'articolo 25, che obbliga le organizzazioni a implementare misure tecniche e organizzative per integrare i principi di protezione dei dati in tutte le attività di trattamento.
        </p>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Caricamento principi Privacy by Design...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Riprova</button>
        </div>
      ) : (
        <div className="pbd-principles-container">
          <h2>I 7 Principi Fondamentali</h2>
          <div className="pbd-principles-list">
            {principles.map((principle) => (
              <div key={principle.id} className="principle-card">
                <h3>{principle.name}</h3>
                <p className="principle-description">{principle.description}</p>
                <div className="examples-section">
                  <h4>Esempi Pratici:</h4>
                  <ul>
                    {principle.examples.map((example, index) => (
                      <li key={index}>{example}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PrivacyByDesignPage;