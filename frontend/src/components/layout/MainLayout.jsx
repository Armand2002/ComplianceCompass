import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import Sidebar from './Sidebar';
import './MainLayout.scss';

const MainLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
  
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    handleResize(); // Imposta lo stato iniziale
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  const closeSidebarOnMobile = () => {
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };
  
  return (
    <div className="main-layout">
      <Header toggleSidebar={toggleSidebar} />
      
      <div className="layout-container">
        <Sidebar open={sidebarOpen} />
        
        {/* Overlay per chiudere la sidebar su mobile */}
        {sidebarOpen && window.innerWidth <= 768 && (
          <div className="sidebar-overlay active" onClick={closeSidebarOnMobile} />
        )}
        
        <main className={`main-content ${sidebarOpen ? 'with-sidebar' : 'without-sidebar'}`}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;