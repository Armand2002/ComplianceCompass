# src/services/notification_service.py
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.user_model import User
from src.models.notification import Notification, NotificationType
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Servizio per la gestione delle notifiche.
    
    Gestisce la creazione, l'invio e la gestione delle notifiche utente.
    """
    
    def __init__(self):
        """Inizializza il servizio notifiche."""
        self.email_service = EmailService()
    
    def create_notification(
        self, 
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        related_object_id: Optional[int] = None,
        related_object_type: Optional[str] = None,
        send_email: bool = False
    ) -> Notification:
        """
        Crea una nuova notifica per un utente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente destinatario
            title (str): Titolo della notifica
            message (str): Messaggio della notifica
            notification_type (NotificationType): Tipo di notifica
            related_object_id (int, optional): ID dell'oggetto correlato
            related_object_type (str, optional): Tipo dell'oggetto correlato
            send_email (bool): Se inviare anche un'email
            
        Returns:
            Notification: Notifica creata
        """
        # Crea notifica
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            created_at=datetime.utcnow(),
            is_read=False
        )
        
        # Salva nel database
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Invia email se richiesto
        if send_email:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                self.email_service.send_notification_email(
                    to_email=user.email,
                    subject=title,
                    message=message,
                    notification_type=notification_type
                )
        
        logger.info(f"Notifica creata per utente {user_id}: {title}")
        return notification
    
    def get_user_notifications(
        self, 
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Recupera le notifiche di un utente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente
            skip (int): Numero di record da saltare
            limit (int): Numero massimo di record da restituire
            unread_only (bool): Se restituire solo notifiche non lette
            
        Returns:
            Dict[str, Any]: Dizionario con notifiche e contatori
        """
        # Query base
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        # Filtra per non lette se richiesto
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Conteggio totale per paginazione
        total = query.count()
        
        # Recupera notifiche con paginazione
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        
        # Conteggio notifiche non lette
        unread_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count
        }
    
    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """
        Marca una notifica come letta.
        
        Args:
            db (Session): Sessione database
            notification_id (int): ID della notifica
            user_id (int): ID dell'utente (per sicurezza)
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        
        return True
    
    def mark_all_as_read(self, db: Session, user_id: int) -> int:
        """
        Marca tutte le notifiche di un utente come lette.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente
            
        Returns:
            int: Numero di notifiche aggiornate
        """
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        return result
    
    def delete_notification(self, db: Session, notification_id: int, user_id: int) -> bool:
        """
        Elimina una notifica.
        
        Args:
            db (Session): Sessione database
            notification_id (int): ID della notifica
            user_id (int): ID dell'utente (per sicurezza)
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        db.delete(notification)
        db.commit()
        
        return True
    
    def notify_pattern_update(
        self, 
        db: Session, 
        pattern_id: int, 
        pattern_title: str, 
        updated_by_id: int
    ) -> None:
        """
        Invia notifiche agli utenti interessati quando un pattern viene aggiornato.
        
        Args:
            db (Session): Sessione database
            pattern_id (int): ID del pattern aggiornato
            pattern_title (str): Titolo del pattern
            updated_by_id (int): ID dell'utente che ha effettuato l'aggiornamento
        """
        # Ottieni utenti che hanno mostrato interesse nel pattern (es. preferiti)
        # Questa è un'implementazione di esempio
        interested_users = db.query(User).filter(User.id != updated_by_id).all()
        
        for user in interested_users:
            self.create_notification(
                db=db,
                user_id=user.id,
                title="Pattern aggiornato",
                message=f"Il pattern '{pattern_title}' è stato aggiornato.",
                notification_type=NotificationType.UPDATE,
                related_object_id=pattern_id,
                related_object_type="pattern",
                send_email=user.email_notifications_enabled if hasattr(user, "email_notifications_enabled") else False
            )