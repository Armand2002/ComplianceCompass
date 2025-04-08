import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import './Header.scss';
import { FaBars, FaEnvelope, FaUser, FaSignOutAlt } from 'react-icons/fa';

export const Header = ({ toggleSidebar, user }) => {
  // Definisci lo stile per le icone con un colore diverso
  const iconStyle = {
    color: '#1976d2', // colore blu primario 
    fontSize: '20px'
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <button className="sidebar-toggle" onClick={toggleSidebar} aria-label="Toggle sidebar">
          <FaBars style={iconStyle} />
        </button>
        
        <Link to="/" className="logo-container">
          <img src="/logo.png" alt="ComplianceCompass Logo" className="logo" />
          <span className="logo-text">ComplianceCompass</span>
        </Link>
      </div>
      
      <div className="header-right">
        {user ? (
          <div className="user-menu">
            <span className="user-name">{user.username}</span>
            <Link to="/profile" className="header-icon">
              <FaUser style={iconStyle} />
            </Link>
            <Link to="/logout" className="header-icon">
              <FaSignOutAlt style={iconStyle} />
            </Link>
          </div>
        ) : (
          <div className="auth-links">
            <Link to="/login" className="auth-link">Accedi</Link>
            <Link to="/register" className="auth-link">Registrati</Link>
          </div>
        )}
      </div>
    </header>
  );
};

const Sidebar = () => {
  const sidebarIconStyle = {
    color: '#1976d2', // colore blu primario
    fontSize: '18px'
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        {/* ... existing header ... */}
      </div>
      <nav className="sidebar-nav">
        <ul>
          {/* ... existing menu items ... */}
          
          <li>
            <NavLink 
              to="/newsletter/manage" 
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <FaEnvelope style={sidebarIconStyle} className="icon" />
              <span>Gestisci Newsletter</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export { Sidebar };