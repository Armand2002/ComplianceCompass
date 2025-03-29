import React, { createContext, useState, useEffect, useContext } from 'react';
import { AuthContext } from './AuthContext';

export const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useContext(AuthContext);
  
  // Carica notifiche quando l'utente è autenticato
  useEffect(() => {
    if (isAuthenticated) {
      loadNotifications();
    }
  }, [isAuthenticated]);
  
  // Funzione per caricare le notifiche
  const loadNotifications = async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      const response = await fetch('/api/notifications?limit=10&unread_only=false');
      
      if (!response.ok) {
        throw new Error('Errore nel caricamento delle notifiche');
      }
      
      const data = await response.json();
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Errore nel caricamento delle notifiche:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Marca una notifica come letta
  const markNotificationRead = async (notificationId) => {
    try {
      const response = await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error('Errore nel marcare la notifica come letta');
      }
      
      // Aggiorna lo stato locale
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId ? { ...notif, read: true } : notif
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Errore nel marcare la notifica come letta:', error);
    }
  };
  
  // Marca tutte le notifiche come lette
  const markAllAsRead = async () => {
    try {
      const response = await fetch('/api/notifications/read-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error('Errore nel marcare tutte le notifiche come lette');
      }
      
      // Aggiorna lo stato locale
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, read: true }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Errore nel marcare tutte le notifiche come lette:', error);
    }
  };
  
  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        loading,
        loadNotifications,
        markNotificationRead,
        markAllAsRead
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};