# src/controllers/notification_controller.py
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.models.notification import Notification, NotificationType
from src.models.user_model import User
from src.services.notification_service import NotificationService

class NotificationController:
    """
    Controller per la gestione delle notifiche.
    
    Gestisce la logica di business per operazioni sulle notifiche.
    """
    
    def __init__(self):
        """Inizializza il controller con il servizio di notifiche."""
        self.notification_service = NotificationService()
    
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
            Dict[str, Any]: Dizionario con notifiche e metadati
        """
        return self.notification_service.get_user_notifications(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            unread_only=unread_only
        )
    
    def mark_notification_read(
        self, 
        db: Session, 
        notification_id: int, 
        current_user: User
    ) -> bool:
        """
        Marca una notifica come letta.
        
        Args:
            db (Session): Sessione database
            notification_id (int): ID della notifica
            current_user (User): Utente corrente
            
        Returns:
            bool: True se l'operazione è riuscita
            
        Raises:
            HTTPException: Se la notifica non esiste o non appartiene all'utente
        """
        result = self.notification_service.mark_as_read(db, notification_id, current_user.id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notifica non trovata o non autorizzata"
            )
        
        return True
    
    def mark_all_notifications_read(self, db: Session, current_user: User) -> int:
        """
        Marca tutte le notifiche di un utente come lette.
        
        Args:
            db (Session): Sessione database
            current_user (User): Utente corrente
            
        Returns:
            int: Numero di notifiche aggiornate
        """
        return self.notification_service.mark_all_as_read(db, current_user.id)
    
    def delete_notification(
        self, 
        db: Session, 
        notification_id: int, 
        current_user: User
    ) -> bool:
        """
        Elimina una notifica.
        
        Args:
            db (Session): Sessione database
            notification_id (int): ID della notifica
            current_user (User): Utente corrente
            
        Returns:
            bool: True se l'operazione è riuscita
            
        Raises:
            HTTPException: Se la notifica non esiste o non appartiene all'utente
        """
        result = self.notification_service.delete_notification(db, notification_id, current_user.id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notifica non trovata o non autorizzata"
            )
        
        return True
    
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
            
        Raises:
            HTTPException: Se l'utente non esiste
        """
        # Verifica che l'utente esista
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utente con ID {user_id} non trovato"
            )
        
        return self.notification_service.create_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            send_email=send_email
        )