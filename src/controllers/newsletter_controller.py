# src/controllers/newsletter_controller.py
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.services.newsletter_service import NewsletterService
from src.models.newsletter import NewsletterSubscription, NewsletterIssue
from src.schemas.newsletter import (
    NewsletterSubscriptionCreate, 
    NewsletterSubscriptionResponse,
    NewsletterIssueCreate,
    NewsletterIssueResponse,
    NewsletterIssueList,
    NewsletterSubscriptionList
)

class NewsletterController:
    """
    Controller per la gestione delle newsletter.
    
    Gestisce le richieste relative alle iscrizioni newsletter e alle edizioni della newsletter.
    """
    def __init__(self):
        self.newsletter_service = NewsletterService()
    
    def subscribe(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Gestisce l'iscrizione alla newsletter.
        
        Args:
            db: Sessione database
            email: Email dell'utente da iscrivere
            
        Returns:
            Dizionario con risultato dell'operazione
        
        Raises:
            HTTPException: Se l'operazione fallisce
        """
        result = self.newsletter_service.subscribe(db, email)
        
        if not result.get("success"):
            if result.get("already_subscribed"):
                # Non è un errore, ma un'informazione utile
                return {
                    "message": result.get("message", "Email già iscritta alla newsletter"),
                    "already_subscribed": True
                }
            
            # Errore durante l'iscrizione
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Errore durante l'iscrizione")
            )
            
        # Iscrizione avvenuta con successo
        return {
            "message": result.get("message", "Iscrizione creata con successo"),
            "requires_verification": result.get("requires_verification", True)
        }
    
    def unsubscribe(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Gestisce la cancellazione dell'iscrizione alla newsletter.
        
        Args:
            db: Sessione database
            email: Email dell'utente da disiscrivere
            
        Returns:
            Dizionario con risultato dell'operazione
            
        Raises:
            HTTPException: Se l'operazione fallisce
        """
        result = self.newsletter_service.unsubscribe(db, email)
        
        if not result.get("success"):
            # Gestione specifica dell'errore "email non trovata"
            if result.get("message") == "Email non trovata":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Email non trovata tra le iscrizioni"
                )
            
            # Altri errori
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Errore durante la cancellazione dell'iscrizione")
            )
            
        return {"message": result.get("message", "Iscrizione cancellata con successo")}
    
    def verify_subscription(self, db: Session, email: str, token: str) -> Dict[str, Any]:
        """
        Gestisce la verifica dell'iscrizione tramite token.
        
        Args:
            db: Sessione database
            email: Email dell'utente
            token: Token di verifica
            
        Returns:
            Dizionario con risultato dell'operazione
            
        Raises:
            HTTPException: Se l'operazione fallisce
        """
        result = self.newsletter_service.verify_subscription(db, email, token)
        
        if not result.get("success"):
            # Token non valido o altro errore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Errore durante la verifica")
            )
            
        # Verifica già effettuata in precedenza (non un errore)
        if result.get("already_verified"):
            return {"message": "Email già verificata"}
            
        return {"message": result.get("message", "Email verificata con successo")}
    
    def get_subscription_status(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Ottiene lo stato dell'iscrizione.
        
        Args:
            db: Sessione database
            email: Email da verificare
            
        Returns:
            Dizionario con lo stato dell'iscrizione
        """
        return self.newsletter_service.get_subscription_status(db, email)
    
    def get_active_subscriptions(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> NewsletterSubscriptionList:
        """
        Ottiene la lista delle iscrizioni attive.
        
        Args:
            db: Sessione database
            skip: Numero di record da saltare
            limit: Numero massimo di record da restituire
            
        Returns:
            Lista delle iscrizioni
        """
        subscriptions = self.newsletter_service.get_active_subscriptions(db, skip, limit)
        
        # Conta il totale per la paginazione
        total = db.query(NewsletterSubscription).filter(
            NewsletterSubscription.is_active == True,
            NewsletterSubscription.is_verified == True
        ).count()
        
        return {
            "items": subscriptions,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit
        }
    
    def create_newsletter_issue(
        self, 
        db: Session, 
        newsletter_data: NewsletterIssueCreate, 
        created_by_id: int
    ) -> NewsletterIssueResponse:
        """
        Crea una nuova edizione della newsletter.
        
        Args:
            db: Sessione database
            newsletter_data: Dati della newsletter
            created_by_id: ID dell'utente che ha creato la newsletter
            
        Returns:
            Dettagli della newsletter creata
            
        Raises:
            HTTPException: Se l'operazione fallisce
        """
        result = self.newsletter_service.create_newsletter_issue(
            db, 
            newsletter_data.subject, 
            newsletter_data.content,
            created_by_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Errore durante la creazione della newsletter")
            )
            
        return result["issue"]
    
    def send_newsletter_issue(self, db: Session, issue_id: int) -> Dict[str, Any]:
        """
        Invia una newsletter a tutti gli iscritti.
        
        Args:
            db: Sessione database
            issue_id: ID della newsletter da inviare
            
        Returns:
            Risultato dell'operazione
            
        Raises:
            HTTPException: Se l'operazione fallisce
        """
        result = self.newsletter_service.send_newsletter_issue(db, issue_id)
        
        if not result.get("success"):
            # Newsletter non trovata
            if result.get("message") == "Newsletter non trovata":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Newsletter non trovata"
                )
                
            # Newsletter già inviata
            if "già inviata" in result.get("message", ""):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Newsletter già inviata in data {result.get('sent_at')}"
                )
                
            # Altri errori
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Errore durante l'invio della newsletter")
            )
            
        return {
            "message": result.get("message"),
            "total_subscribers": result.get("total_subscribers", 0),
            "successful_sends": result.get("successful_sends", 0),
            "failed_sends": result.get("failed_sends", 0)
        }

# Crea un'istanza singleton del controller
newsletter_controller = NewsletterController()