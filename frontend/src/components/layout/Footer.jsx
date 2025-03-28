import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4>Compliance Compass</h4>
          <p>Piattaforma wiki collaborativa per normative tecniche e di sicurezza</p>
        </div>
        
        <div className="footer-section">
          <h4>Link rapidi</h4>
          <ul>
            <li><Link to="/patterns">Privacy Patterns</Link></li>
            <li><Link to="/search">Ricerca</Link></li>
            <li><Link to="/chatbot">Chatbot</Link></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Contatti</h4>
          <ul>
            <li><a href="mailto:info@compliancecompass.example.com">info@compliancecompass.example.com</a></li>
            <li><a href="https://github.com/username/compliance-compass" target="_blank" rel="noopener noreferrer">GitHub</a></li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; {currentYear} Compliance Compass. Tutti i diritti riservati.</p>
        <div className="footer-links">
          <Link to="/privacy-policy">Privacy Policy</Link>
          <Link to="/terms">Termini e Condizioni</Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;