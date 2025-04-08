import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { FaHome, FaList, FaSearch, FaRobot, FaUser, FaPlus, FaChartBar, FaShieldAlt, FaBook, FaEnvelope } from 'react-icons/fa';
import { AuthContext } from '../../context/AuthContext';

const Sidebar = ({ open }) => {
  const { user } = useContext(AuthContext);
  
  return (
    <aside className={`sidebar ${open ? 'open' : 'closed'}`}>
      <div className="sidebar-content">
        <nav className="sidebar-nav">
          <ul>
            <li>
              <NavLink to="/" className={({isActive}) => isActive ? 'active' : ''}>
                <FaHome className="nav-icon" />
                <span className="nav-text">Home</span>
              </NavLink>
            </li>
            
            <li>
              <NavLink to="/patterns" className={({isActive}) => isActive ? 'active' : ''}>
                <FaList className="nav-icon" />
                <span className="nav-text">Privacy Patterns</span>
              </NavLink>
            </li>
            
            <li>
              <NavLink to="/search" className={({isActive}) => isActive ? 'active' : ''}>
                <FaSearch className="nav-icon" />
                <span className="nav-text">Ricerca</span>
              </NavLink>
            </li>
            
            {/* Elementi che richiedono autenticazione */}
            {user && (
              <>
                <li>
                  <NavLink to="/patterns/create" className={({isActive}) => isActive ? 'active' : ''}>
                    <FaPlus className="nav-icon" />
                    <span className="nav-text">Nuovo Pattern</span>
                  </NavLink>
                </li>
                
                <li>
                  <NavLink to="/chatbot" className={({isActive}) => isActive ? 'active' : ''}>
                    <FaRobot className="nav-icon" />
                    <span className="nav-text">Chatbot</span>
                  </NavLink>
                </li>
              </>
            )}
            
            {/* Sezione Risorse - accessibile a tutti */}
            <div className="sidebar-divider"></div>
            <h3 className="sidebar-heading">Risorse</h3>
            <ul>
              <li>
                <NavLink to="/gdpr" className={({isActive}) => isActive ? 'active' : ''}>
                  <FaShieldAlt className="nav-icon" />
                  <span className="nav-text">GDPR</span>
                </NavLink>
              </li>
              
              <li>
                <NavLink to="/privacy-by-design" className={({isActive}) => isActive ? 'active' : ''}>
                  <FaBook className="nav-icon" />
                  <span className="nav-text">Privacy by Design</span>
                </NavLink>
              </li>
              
              <li>
                <NavLink to="/newsletter/manage" className={({isActive}) => isActive ? 'active' : ''}>
                  <FaEnvelope className="nav-icon" />
                  <span className="nav-text">Gestisci Newsletter</span>
                </NavLink>
              </li>
            </ul>
            
            {/* Sezione Utente - solo per utenti autenticati */}
            {user && (
              <>
                <div className="sidebar-divider"></div>
                <h3 className="sidebar-heading">Area Utente</h3>
                <ul>
                  <li>
                    <NavLink to="/dashboard" className={({isActive}) => isActive ? 'active' : ''}>
                      <FaChartBar className="nav-icon" />
                      <span className="nav-text">Dashboard</span>
                    </NavLink>
                  </li>
                  
                  <li>
                    <NavLink to="/profile" className={({isActive}) => isActive ? 'active' : ''}>
                      <FaUser className="nav-icon" />
                      <span className="nav-text">Profilo</span>
                    </NavLink>
                  </li>
                </ul>
              </>
            )}
          </ul>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;