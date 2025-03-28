import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  FaHome, 
  FaList, 
  FaSearch, 
  FaRobot, 
  FaUser, 
  FaPlus, 
  FaChartBar,
  FaShieldAlt,
  FaBook
} from 'react-icons/fa';
import { AuthContext } from '../../context/AuthContext';

const Sidebar = ({ open }) => {
  const { user } = useContext(AuthContext);
  
  // Verifica se l'utente è admin o editor
  const canCreatePattern = user?.role === 'admin' || user?.role === 'editor';

  return (
    <aside className={`sidebar ${open ? 'open' : 'closed'}`}>
      <div className="sidebar-content">
        <nav className="sidebar-nav">
          <ul>
            <li>
              <NavLink to="/dashboard" className={({isActive}) => isActive ? 'active' : ''}>
                <FaHome className="nav-icon" />
                <span className="nav-text">Dashboard</span>
              </NavLink>
            </li>
            
            <li>
              <NavLink to="/patterns" className={({isActive}) => isActive ? 'active' : ''}>
                <FaList className="nav-icon" />
                <span className="nav-text">Privacy Patterns</span>
              </NavLink>
            </li>
            
            {canCreatePattern && (
              <li>
                <NavLink to="/patterns/create" className={({isActive}) => isActive ? 'active' : ''}>
                  <FaPlus className="nav-icon" />
                  <span className="nav-text">Nuovo Pattern</span>
                </NavLink>
              </li>
            )}
            
            <li>
              <NavLink to="/search" className={({isActive}) => isActive ? 'active' : ''}>
                <FaSearch className="nav-icon" />
                <span className="nav-text">Ricerca Avanzata</span>
              </NavLink>
            </li>
            
            <li>
              <NavLink to="/chatbot" className={({isActive}) => isActive ? 'active' : ''}>
                <FaRobot className="nav-icon" />
                <span className="nav-text">Chatbot</span>
              </NavLink>
            </li>
          </ul>
          
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
              <NavLink to="/statistics" className={({isActive}) => isActive ? 'active' : ''}>
                <FaChartBar className="nav-icon" />
                <span className="nav-text">Statistiche</span>
              </NavLink>
            </li>
          </ul>
          
          <div className="sidebar-divider"></div>
          
          <ul>
            <li>
              <NavLink to="/profile" className={({isActive}) => isActive ? 'active' : ''}>
                <FaUser className="nav-icon" />
                <span className="nav-text">Profilo Utente</span>
              </NavLink>
            </li>
          </ul>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;