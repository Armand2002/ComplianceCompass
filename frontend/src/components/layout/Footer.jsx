import React from 'react';
import { Link } from 'react-router-dom';
import NewsletterSubscription from '../newsletter/NewsletterSubscription';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer">
      <div className="container">
        <div className="row">
          <div className="col-md-4">
            <div className="footer-section">
              <h4>Compliance Compass</h4>
              <p>Piattaforma wiki collaborativa per normative tecniche e di sicurezza</p>
            </div>
          </div>
          
          <div className="col-md-4">
            <div className="footer-section">
              <h4>Link rapidi</h4>
              <ul>
                <li><Link to="/patterns">Privacy Patterns</Link></li>
                <li><Link to="/search">Ricerca</Link></li>
                <li><Link to="/chatbot">Chatbot</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="col-md-4">
            <div className="footer-section">
              <h4>Contatti</h4>
              <ul>
                <li><a href="mailto:info@compliancecompass.example.com">info@compliancecompass.example.com</a></li>
                <li><a href="https://github.com/username/compliance-compass" target="_blank" rel="noopener noreferrer">GitHub</a></li>
              </ul>
            </div>
          </div>
          
          <div className="col-md-4">
            <NewsletterSubscription />
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="copyright">
            &copy; {currentYear} ComplianceCompass. All rights reserved.
          </div>
          <div className="footer-links">
            <Link to="/privacy-policy">Privacy Policy</Link>
            <Link to="/terms">Terms of Service</Link>
            <Link to="/newsletter/manage">Gestisci iscrizione newsletter</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;