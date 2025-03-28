import React from 'react';
import { FaShieldAlt, FaBook, FaUsers, FaLightbulb } from 'react-icons/fa';

const AboutPage = () => {
  return (
    <div className="page-container about-page">
      <div className="page-header text-center">
        <div className="header-content mx-auto">
          <h1>Informazioni su Compliance Compass</h1>
          <p>Una piattaforma collaborativa per semplificare la comprensione delle normative tecniche e di sicurezza</p>
        </div>
      </div>
      
      {/* Mission Section */}
      <div className="about-section mission-section">
        <div className="section-flex">
          <div className="section-half primary-bg">
            <h2>La Nostra Missione</h2>
            <p>
              Compliance Compass nasce con l'obiettivo di democratizzare l'accesso alle normative sulla privacy e sicurezza informatica,
              rendendo più semplice per sviluppatori, designer e professionisti IT implementare soluzioni conformi.
            </p>
            <p>
              Attraverso la raccolta e sistematizzazione di pattern di privacy, articoli del GDPR e best practice,
              vogliamo creare un punto di riferimento unico per chi deve navigare nel complesso mondo della compliance.
            </p>
          </div>
          <div className="section-half">
            <h2>I Nostri Obiettivi</h2>
            <ul className="objectives-list">
              <li>
                <span className="icon-container">
                  <FaShieldAlt />
                </span>
                <span>Creare un repository centralizzato di normative tecniche e di sicurezza</span>
              </li>
              <li>
                <span className="icon-container">
                  <FaBook />
                </span>
                <span>Offrire interpretazioni pratiche e casi d'uso reali</span>
              </li>
              <li>
                <span className="icon-container">
                  <FaUsers />
                </span>
                <span>Costruire una comunità di esperti e professionisti della privacy</span>
              </li>
              <li>
                <span className="icon-container">
                  <FaLightbulb />
                </span>
                <span>Facilitare l'innovazione senza compromettere la privacy</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Privacy Patterns */}
      <div className="about-section patterns-section">
        <h2>Cosa sono i Privacy Patterns?</h2>
        <div className="content-card">
          <p>
            I Privacy Patterns sono soluzioni riutilizzabili per affrontare problemi comuni di privacy nella progettazione di sistemi software.
            Simili ai design pattern nell'ingegneria del software, i privacy pattern offrono template collaudati per implementare
            funzionalità nel rispetto della privacy degli utenti.
          </p>
          
          <p>
            Ogni pattern in Compliance Compass è documentato con:
          </p>
          
          <div className="pattern-features">
            <div className="feature-item">
              <h3>Contesto</h3>
              <p>Quando e perché applicare questo pattern</p>
            </div>
            <div className="feature-item">
              <h3>Problema</h3>
              <p>La sfida di privacy che il pattern affronta</p>
            </div>
            <div className="feature-item">
              <h3>Soluzione</h3>
              <p>Come implementare il pattern nel proprio sistema</p>
            </div>
            <div className="feature-item">
              <h3>Conseguenze</h3>
              <p>Vantaggi e potenziali limiti dell'approccio</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Team Section */}
      <div className="about-section team-section">
        <h2>Il Nostro Team</h2>
        <p className="text-center">
          Compliance Compass è sviluppato da un team di esperti in sicurezza informatica, normative sulla privacy e sviluppo software.
        </p>
        
        <div className="team-grid">
          <div className="team-member">
            <div className="member-avatar"></div>
            <h3>Mario Rossi</h3>
            <p>Privacy Specialist</p>
          </div>
          <div className="team-member">
            <div className="member-avatar"></div>
            <h3>Laura Bianchi</h3>
            <p>Software Architect</p>
          </div>
          <div className="team-member">
            <div className="member-avatar"></div>
            <h3>Giuseppe Verdi</h3>
            <p>Security Consultant</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;