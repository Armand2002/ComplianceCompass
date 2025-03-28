import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaBars, FaBell, FaUser, FaSearch, FaSignOutAlt } from 'react-icons/fa';
import { AuthContext } from '../../context/AuthContext';

const Header = ({ toggleSidebar, user }) => {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Toggle del dropdown utente
  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  // Gestione del logout
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Gestione della ricerca
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <button className="sidebar-toggle" onClick={toggleSidebar}>
          <FaBars />
        </button>
        <Link to="/" className="logo">
          <img src="/assets/images/logo.png" alt="Compliance Compass" />
          <span>Compliance Compass</span>
        </Link>
      </div>

      <div className="header-search">
        <form onSubmit={handleSearch}>
          <div className="search-input-container">
            <FaSearch className="search-icon" />
            <input 
              type="text" 
              placeholder="Cerca pattern, articoli GDPR..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </form>
      </div>

      <div className="header-right">
        <div className="notification-icon">
          <Link to="/notifications">
            <FaBell />
            {/* Badge per le notifiche non lette */}
            <span className="notification-badge">3</span>
          </Link>
        </div>

        <div className="user-profile">
          <button className="profile-button" onClick={toggleDropdown}>
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.username} className="avatar" />
            ) : (
              <FaUser className="avatar-icon" />
            )}
            <span className="username">{user?.username || 'Utente'}</span>
          </button>

          {dropdownOpen && (
            <div className="profile-dropdown">
              <ul>
                <li>
                  <Link to="/profile">
                    <FaUser />
                    <span>Profilo</span>
                  </Link>
                </li>
                <li>
                  <button onClick={handleLogout} className="logout-button">
                    <FaSignOutAlt />
                    <span>Logout</span>
                  </button>
                </li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;